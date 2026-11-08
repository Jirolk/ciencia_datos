"""Orquestación con Dagster del pipeline del minimercado.

Assets (en orden de dependencia):
    generar_datos_asset -> ingesta_dlt_asset -> dbt_transformations_asset -> reporte_calidad_asset

Ejecución:
    # Interfaz web (Materialize all)
    dagster dev -f orchestration/definitions.py

    # Línea de comandos
    dagster asset materialize --select "*" -f orchestration/definitions.py
    dagster job execute -j pipeline_completo -f orchestration/definitions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dagster import (
    AssetSelection,
    Definitions,
    Failure,
    MaterializeResult,
    MetadataValue,
    asset,
    define_asset_job,
)

# Permite importar los módulos de la raíz del equipo (generar_datos, pipeline, analisis)
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import analisis  # noqa: E402
import generar_datos  # noqa: E402
import pipeline  # noqa: E402

GRUPO = "minimercado"


@asset(group_name=GRUPO, description="Genera los CSV sintéticos (semilla fija) en data/.")
def generar_datos_asset() -> MaterializeResult:
    resumen = generar_datos.main([])  # usa seed=42 y escribe en ./data
    return MaterializeResult(metadata={t: MetadataValue.int(n) for t, n in resumen.items()})


@asset(
    group_name=GRUPO,
    deps=[generar_datos_asset],
    description="Carga idempotente de los CSV a DuckDB (esquema raw) con dlt.",
)
def ingesta_dlt_asset() -> MaterializeResult:
    pipeline.ejecutar_ingesta()
    filas = pipeline.contar_filas()
    return MaterializeResult(metadata={t: MetadataValue.int(n) for t, n in filas.items()})


@asset(
    group_name=GRUPO,
    deps=[ingesta_dlt_asset],
    description="Ejecuta `dbt build`: construye staging/intermediate/marts y corre las pruebas.",
)
def dbt_transformations_asset() -> MaterializeResult:
    try:
        pipeline.ejecutar_dbt(comando="build")
    except RuntimeError as exc:
        raise Failure(description=str(exc)) from exc
    return MaterializeResult(
        metadata={"comando": "dbt build", "proyecto": MetadataValue.path(str(pipeline.DBT_DIR))}
    )


@asset(
    group_name=GRUPO,
    deps=[dbt_transformations_asset],
    description="Valida la salida final (volúmenes, duplicados, conciliaciones, stock, ABC).",
)
def reporte_calidad_asset() -> MaterializeResult:
    reporte = analisis.generar_reporte_calidad()
    ruta = analisis.escribir_reporte(reporte)
    fallidos = [c for c in reporte["checks"] if not c["ok"]]
    if fallidos:
        raise Failure(
            description=f"{len(fallidos)} validaciones de calidad fallaron",
            metadata={c["check"]: c["detalle"] for c in fallidos},
        )
    return MaterializeResult(
        metadata={
            "validaciones_ok": len(reporte["checks"]),
            "reporte": MetadataValue.path(str(ruta)),
        }
    )


pipeline_completo = define_asset_job(
    name="pipeline_completo",
    selection=AssetSelection.groups(GRUPO),
    description="Ejecuta de punta a punta: datos -> dlt -> dbt -> reporte de calidad.",
)

defs = Definitions(
    assets=[
        generar_datos_asset,
        ingesta_dlt_asset,
        dbt_transformations_asset,
        reporte_calidad_asset,
    ],
    jobs=[pipeline_completo],
)
