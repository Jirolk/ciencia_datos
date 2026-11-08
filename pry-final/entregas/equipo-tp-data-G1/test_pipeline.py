"""Pruebas automatizadas del pipeline del minimercado."""

from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import dagster as dg
import duckdb
import pytest

import generar_datos
import pipeline

CARPETA = Path(__file__).resolve().parent
TABLAS = ["productos", "vendedores", "compras", "ventas", "movimientos_stock"]
COLUMNAS = {
    "productos": {"id", "nombre", "categoria", "costo_unitario", "precio_venta", "stock_inicial"},
    "vendedores": {"id", "nombre", "sucursal", "fecha_alta"},
    "compras": {"id", "fecha", "producto_id", "cantidad", "costo_unitario", "proveedor"},
    "ventas": {
        "id",
        "fecha",
        "producto_id",
        "cantidad",
        "precio_unitario",
        "descuento",
        "vendedor_id",
    },
    "movimientos_stock": {"id", "fecha", "producto_id", "tipo", "cantidad", "referencia"},
}


@pytest.fixture(autouse=True)
def estado_dlt_temporal(tmp_path, monkeypatch):
    """dlt guarda su estado en ~/.dlt; en las pruebas lo mandamos a una carpeta temporal."""
    monkeypatch.setenv("DLT_DATA_DIR", str(tmp_path / "dlt"))


# ---------------------------------------------------------------------------
# 1. Reproducibilidad de la generación de datos
# ---------------------------------------------------------------------------
def test_misma_semilla_mismos_datos():
    assert generar_datos.generar(42) == generar_datos.generar(42)


def test_otra_semilla_otros_datos():
    assert generar_datos.generar(42)["ventas"] != generar_datos.generar(7)["ventas"]


def test_csv_reproducibles(tmp_path):
    """Escribir dos veces con la misma semilla produce archivos idénticos byte a byte."""
    for carpeta in ("a", "b"):
        generar_datos.escribir_csv(generar_datos.generar(42), tmp_path / carpeta)
    for tabla in TABLAS:
        archivo = f"{tabla}.csv"
        assert (tmp_path / "a" / archivo).read_bytes() == (tmp_path / "b" / archivo).read_bytes()


def test_volumenes_minimos_y_consistencia():
    datos = generar_datos.generar(42)
    productos = {p["id"]: p for p in datos["productos"]}
    vendedores = {v["id"] for v in datos["vendedores"]}

    assert len(productos) == 20
    assert len(vendedores) == 5
    assert len(datos["compras"]) >= 100
    assert len(datos["ventas"]) >= 500
    fechas = sorted({date.fromisoformat(v["fecha"]) for v in datos["ventas"]})
    assert (fechas[-1] - fechas[0]).days + 1 >= 90

    for venta in datos["ventas"]:
        assert venta["producto_id"] in productos
        assert venta["vendedor_id"] in vendedores
        assert venta["cantidad"] > 0 and venta["precio_unitario"] > 0
    for compra in datos["compras"]:
        assert compra["producto_id"] in productos
        assert compra["cantidad"] > 0 and compra["costo_unitario"] > 0

    # Recorriendo los movimientos en orden, el stock nunca queda negativo.
    stock = {pid: p["stock_inicial"] for pid, p in productos.items()}
    for mov in datos["movimientos_stock"]:
        signo = 1 if mov["tipo"] == "entrada" else -1
        stock[mov["producto_id"]] += signo * mov["cantidad"]
        assert stock[mov["producto_id"]] >= 0


# ---------------------------------------------------------------------------
# 2. Esquema en DuckDB tras la ingesta con dlt
# ---------------------------------------------------------------------------
def _ingestar(carpeta_datos: Path, ruta_db: Path) -> None:
    info = pipeline.construir_pipeline(ruta_db).run(pipeline.minimercado(carpeta_datos))
    info.raise_on_failed_jobs()


@pytest.fixture()
def base_cargada(tmp_path) -> tuple[Path, dict]:
    datos = generar_datos.generar(42)
    generar_datos.escribir_csv(datos, tmp_path / "data")
    ruta_db = tmp_path / "prueba.duckdb"
    _ingestar(tmp_path / "data", ruta_db)
    return ruta_db, datos


def test_esquema_en_duckdb(base_cargada):
    ruta_db, datos = base_cargada
    with duckdb.connect(str(ruta_db), read_only=True) as con:
        for tabla in TABLAS:
            columnas = {
                fila[0]
                for fila in con.execute(
                    "select column_name from information_schema.columns "
                    "where table_schema = ? and table_name = ?",
                    [pipeline.DATASET, tabla],
                ).fetchall()
            }
            assert columnas, f"no existe {pipeline.DATASET}.{tabla}"
            assert COLUMNAS[tabla] <= columnas, f"faltan columnas en {tabla}"
            assert {"_dlt_load_id", "_dlt_id"} <= columnas

            filas = con.execute(f"select count(*) from {pipeline.DATASET}.{tabla}").fetchone()[0]
            assert filas == len(datos[tabla])


def test_ingesta_idempotente(base_cargada, tmp_path):
    ruta_db, datos = base_cargada
    _ingestar(tmp_path / "data", ruta_db)  # segunda ejecución sobre la misma base

    with duckdb.connect(str(ruta_db), read_only=True) as con:
        for tabla in TABLAS:
            total, distintos = con.execute(
                f"select count(*), count(distinct id) from {pipeline.DATASET}.{tabla}"
            ).fetchone()
            assert total == distintos == len(datos[tabla]), f"{tabla}: hay filas duplicadas"


# ---------------------------------------------------------------------------
# 3. Punta a punta: el job completo de Dagster
# ---------------------------------------------------------------------------
def _cargar_definiciones() -> dg.Definitions:
    ruta = CARPETA / "orchestration" / "definitions.py"
    spec = importlib.util.spec_from_file_location("definiciones_minimercado", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.defs


def test_punta_a_punta_con_dagster(tmp_path, monkeypatch):
    ruta_db = tmp_path / "e2e.duckdb"
    reporte = tmp_path / "reporte_calidad.json"
    monkeypatch.setenv("MINIMERCADO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("DUCKDB_PATH", str(ruta_db))
    monkeypatch.setenv("REPORTE_CALIDAD_PATH", str(reporte))
    monkeypatch.setenv("DBT_TARGET_PATH", str(tmp_path / "dbt_target"))
    monkeypatch.setenv("DBT_LOG_PATH", str(tmp_path / "dbt_logs"))

    job = _cargar_definiciones().resolve_job_def("pipeline_completo_job")
    resultado = job.execute_in_process(instance=dg.DagsterInstance.ephemeral())

    assert resultado.success
    materializados = {e.asset_key.path[-1] for e in resultado.get_asset_materialization_events()}
    assert materializados == {
        "generar_datos_asset",
        "ingesta_dlt_asset",
        "dbt_transformations_asset",
        "reporte_calidad_asset",
    }

    contenido = json.loads(reporte.read_text(encoding="utf-8"))
    assert contenido["aprobado"], contenido["fallidos"]

    with duckdb.connect(str(ruta_db), read_only=True) as con:
        for tabla in [
            "mart_ventas_diarias",
            "mart_rentabilidad_productos",
            "mart_rotacion_inventario",
            "mart_desempeno_vendedores",
            "mart_clasificacion_abc",
        ]:
            assert con.execute(f"select count(*) from analytics.{tabla}").fetchone()[0] > 0

        # La facturación de los marts coincide con la calculada directamente desde los datos.
        facturacion_mart = con.execute(
            "select sum(facturacion) from analytics.mart_ventas_diarias"
        ).fetchone()[0]
    ventas = generar_datos.generar(42)["ventas"]
    facturacion_python = sum(
        v["cantidad"] * v["precio_unitario"] * (1 - v["descuento"]) for v in ventas
    )
    assert abs(float(facturacion_mart) - facturacion_python) < 1
