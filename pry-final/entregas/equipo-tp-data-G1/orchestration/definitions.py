"""Orquestación del pipeline del minimercado con Dagster."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import dagster as dg
import duckdb

CARPETA_EQUIPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARPETA_EQUIPO))

import generar_datos  # noqa: E402
import pipeline  # noqa: E402

DIR_DBT = CARPETA_EQUIPO / "dbt_project"
ESQUEMA_RAW = pipeline.DATASET  # raw_minimercado
ESQUEMA_DBT = "analytics"  # esquema definido en dbt_project/profiles.yml
TABLAS_FINALES = [
    "mart_ventas_diarias",
    "mart_rentabilidad_productos",
    "mart_rotacion_inventario",
    "mart_desempeno_vendedores",
    "mart_clasificacion_abc",
]


def rutas() -> dict[str, Path]:
    """Rutas de trabajo. Se leen en cada ejecución para poder cambiarlas en las pruebas."""
    return {
        "data": Path(os.environ.get("MINIMERCADO_DATA_DIR", generar_datos.DIR_DATA)),
        "duckdb": Path(os.environ.get("DUCKDB_PATH", pipeline.RUTA_DB)),
        "reporte": Path(
            os.environ.get("REPORTE_CALIDAD_PATH", CARPETA_EQUIPO / "reporte_calidad.json")
        ),
    }


# ---------------------------------------------------------------------------
# 1. Generación de datos sintéticos
# ---------------------------------------------------------------------------
class ConfigGeneracion(dg.Config):
    semilla: int = generar_datos.SEMILLA


@dg.asset(
    group_name="generacion",
    kinds={"python"},
    description="Genera los 5 CSV sintéticos del minimercado en data/ con semilla fija.",
)
def generar_datos_asset(
    context: dg.AssetExecutionContext, config: ConfigGeneracion
) -> dg.MaterializeResult:
    carpeta = rutas()["data"]
    datos = generar_datos.generar(config.semilla)
    generar_datos.escribir_csv(datos, carpeta)
    filas = {nombre: len(registros) for nombre, registros in datos.items()}
    context.log.info(f"CSV generados en {carpeta}: {filas}")
    return dg.MaterializeResult(
        metadata={"semilla": config.semilla, **{f"filas_{k}": v for k, v in filas.items()}}
    )


# ---------------------------------------------------------------------------
# 2. Ingesta con dlt hacia DuckDB
# ---------------------------------------------------------------------------
@dg.asset(
    group_name="ingesta",
    deps=[generar_datos_asset],
    kinds={"dlt", "duckdb"},
    description="Carga los CSV a data.duckdb (esquema raw_minimercado) sin duplicar filas.",
)
def ingesta_dlt_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    r = rutas()
    info = pipeline.construir_pipeline(r["duckdb"]).run(pipeline.minimercado(r["data"]))
    info.raise_on_failed_jobs()

    with duckdb.connect(str(r["duckdb"]), read_only=True) as con:
        filas = {
            tabla: con.execute(f"select count(*) from {ESQUEMA_RAW}.{tabla}").fetchone()[0]
            for tabla in pipeline.TABLAS
        }
    context.log.info(f"Filas en {ESQUEMA_RAW}: {filas}")
    return dg.MaterializeResult(metadata={f"filas_{k}": v for k, v in filas.items()})


# ---------------------------------------------------------------------------
# 3. Transformaciones y pruebas con dbt
# ---------------------------------------------------------------------------
@dg.asset(
    group_name="transformacion",
    deps=[ingesta_dlt_asset],
    kinds={"dbt", "duckdb"},
    description="Ejecuta `dbt build`: modelos staging, intermediate y marts junto con sus pruebas.",
)
def dbt_transformations_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    dbt = shutil.which("dbt") or str(Path(sys.executable).parent / "dbt")
    comando = [dbt, "build", "--project-dir", str(DIR_DBT), "--profiles-dir", str(DIR_DBT)]
    # La ruta absoluta evita que dbt busque la base en otra carpeta.
    entorno = {**os.environ, "DUCKDB_PATH": str(rutas()["duckdb"])}

    resultado = subprocess.run(comando, env=entorno, capture_output=True, text=True, check=False)
    for linea in resultado.stdout.splitlines():
        context.log.info(linea)
    if resultado.returncode != 0:
        raise dg.Failure(
            description="dbt build falló: algún modelo o prueba tiene errores.",
            metadata={"salida": dg.MetadataValue.text(resultado.stdout[-4000:])},
        )

    resumen = next((x for x in resultado.stdout.splitlines() if "PASS=" in x), "")
    return dg.MaterializeResult(metadata={"resumen_dbt": resumen.strip()})


# ---------------------------------------------------------------------------
# 4. Reporte de calidad de la salida final
# ---------------------------------------------------------------------------
# Cada control es una consulta que devuelve verdadero si los datos están bien.
CONTROLES = {
    "minimo_20_productos": f"select count(*) = 20 from {ESQUEMA_RAW}.productos",
    "minimo_5_vendedores": f"select count(*) = 5 from {ESQUEMA_RAW}.vendedores",
    "minimo_100_compras": f"select count(*) >= 100 from {ESQUEMA_RAW}.compras",
    "minimo_500_ventas": f"select count(*) >= 500 from {ESQUEMA_RAW}.ventas",
    "minimo_90_dias": f"select count(*) >= 90 from {ESQUEMA_DBT}.mart_ventas_diarias",
    "sin_ventas_duplicadas": f"select count(*) = count(distinct id) from {ESQUEMA_RAW}.ventas",
    "todas_las_ventas_llegan_al_mart": (
        f"select (select count(*) from {ESQUEMA_RAW}.ventas)"
        f" = (select sum(cantidad_ventas) from {ESQUEMA_DBT}.mart_ventas_diarias)"
    ),
    "facturacion_igual_en_marts_diario_y_productos": (
        f"select abs((select sum(facturacion) from {ESQUEMA_DBT}.mart_ventas_diarias)"
        f" - (select sum(ingresos) from {ESQUEMA_DBT}.mart_rentabilidad_productos)) < 1"
    ),
    "facturacion_igual_en_marts_diario_y_vendedores": (
        f"select abs((select sum(facturacion) from {ESQUEMA_DBT}.mart_ventas_diarias)"
        f" - (select sum(facturacion) from {ESQUEMA_DBT}.mart_desempeno_vendedores)) < 1"
    ),
    "stock_nunca_negativo": (
        f"select min(stock_despues) >= 0 from {ESQUEMA_DBT}.int_movimientos_stock"
    ),
    "abc_suma_100_por_ciento": (
        f"select abs(sum(participacion_pct) - 100) < 0.1 from {ESQUEMA_DBT}.mart_clasificacion_abc"
    ),
    "abc_tiene_las_tres_clases": (
        f"select count(distinct clase_abc) = 3 from {ESQUEMA_DBT}.mart_clasificacion_abc"
    ),
}


@dg.asset(
    group_name="calidad",
    deps=[dbt_transformations_asset],
    kinds={"duckdb"},
    description="Valida la salida final y guarda el resultado en reporte_calidad.json.",
)
def reporte_calidad_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    r = rutas()
    with duckdb.connect(str(r["duckdb"]), read_only=True) as con:
        filas_finales = {
            tabla: con.execute(f"select count(*) from {ESQUEMA_DBT}.{tabla}").fetchone()[0]
            for tabla in TABLAS_FINALES
        }
        controles = {
            nombre: bool(con.execute(sql).fetchone()[0]) for nombre, sql in CONTROLES.items()
        }
        facturacion = con.execute(
            f"select round(sum(facturacion)) from {ESQUEMA_DBT}.mart_ventas_diarias"
        ).fetchone()[0]

    controles.update({f"{t}_tiene_filas": n > 0 for t, n in filas_finales.items()})
    fallidos = [nombre for nombre, ok in controles.items() if not ok]
    reporte = {
        "aprobado": not fallidos,
        "fallidos": fallidos,
        "controles": controles,
        "filas_tablas_finales": filas_finales,
        "facturacion_total": float(facturacion),
    }
    r["reporte"].write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")

    for nombre, ok in controles.items():
        context.log.info(f"{'OK   ' if ok else 'FALLA'} {nombre}")
    if fallidos:
        raise dg.Failure(description=f"Controles de calidad fallidos: {fallidos}")

    return dg.MaterializeResult(
        metadata={
            "controles_aprobados": f"{len(controles)}/{len(controles)}",
            "facturacion_total": float(facturacion),
            "reporte": str(r["reporte"]),
        }
    )


# ---------------------------------------------------------------------------
# Job, schedule y Definitions
# ---------------------------------------------------------------------------
pipeline_completo_job = dg.define_asset_job(
    "pipeline_completo_job",
    selection=dg.AssetSelection.all(),
    description="Generación -> ingesta -> dbt -> reporte de calidad.",
)

carga_nocturna = dg.ScheduleDefinition(
    job=pipeline_completo_job,
    cron_schedule="0 2 * * *",
    execution_timezone="America/Asuncion",
    default_status=dg.DefaultScheduleStatus.STOPPED,  # se activa en la pestaña Automation
)

defs = dg.Definitions(
    assets=[
        generar_datos_asset,
        ingesta_dlt_asset,
        dbt_transformations_asset,
        reporte_calidad_asset,
    ],
    jobs=[pipeline_completo_job],
    schedules=[carga_nocturna],
)
