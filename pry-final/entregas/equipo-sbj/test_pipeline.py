"""Suite de pruebas del pipeline del minimercado.

    pytest -v                 # todo (el E2E tarda ~15 s)
    pytest -v -k "not e2e"    # solo pruebas rápidas

Todas las pruebas trabajan en carpetas temporales: no tocan data/ ni data.duckdb.
"""

from __future__ import annotations

import hashlib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import analisis
import duckdb
import generar_datos
import pipeline
import pytest

TABLAS = ["productos", "vendedores", "compras", "ventas", "movimientos_stock"]


def _hashes(carpeta: Path) -> dict[str, str]:
    return {t: hashlib.sha256((carpeta / f"{t}.csv").read_bytes()).hexdigest() for t in TABLAS}


# --------------------------------------------------------------------------- #
# 1. Generación de datos
# --------------------------------------------------------------------------- #
def test_generacion_reproducible_con_misma_semilla(tmp_path):
    generar_datos.main(["--seed", "42", "--salida", str(tmp_path / "a")])
    generar_datos.main(["--seed", "42", "--salida", str(tmp_path / "b")])
    assert _hashes(tmp_path / "a") == _hashes(tmp_path / "b")


def test_semillas_distintas_generan_datos_distintos(tmp_path):
    generar_datos.main(["--seed", "1", "--salida", str(tmp_path / "a")])
    generar_datos.main(["--seed", "2", "--salida", str(tmp_path / "b")])
    assert _hashes(tmp_path / "a")["ventas"] != _hashes(tmp_path / "b")["ventas"]


def test_volumenes_y_cobertura_minimos():
    d = generar_datos.generar()
    assert len(d["productos"]) == 20
    assert len(d["vendedores"]) == 5
    assert len(d["compras"]) >= 100
    assert len(d["ventas"]) >= 500
    assert len({v["fecha"] for v in d["ventas"]}) >= 90


def test_consistencia_referencial_e_importes_positivos():
    d = generar_datos.generar()
    pids = {p["id"] for p in d["productos"]}
    vids = {v["id"] for v in d["vendedores"]}
    assert {v["producto_id"] for v in d["ventas"]} <= pids
    assert {v["vendedor_id"] for v in d["ventas"]} <= vids
    assert {c["producto_id"] for c in d["compras"]} <= pids
    assert all(v["cantidad"] > 0 and v["precio_unitario"] > 0 for v in d["ventas"])
    assert all(c["cantidad"] > 0 and c["costo_unitario"] > 0 for c in d["compras"])
    # ids únicos en todas las tablas
    for tabla, filas in d.items():
        ids = [f["id"] for f in filas]
        assert len(ids) == len(set(ids)), f"ids repetidos en {tabla}"


def test_stock_nunca_negativo_y_movimientos_cuadran_con_operaciones():
    d = generar_datos.generar()
    saldo: dict[int, int] = {}
    for m in d["movimientos_stock"]:
        saldo[m["producto_id"]] = saldo.get(m["producto_id"], 0) + (
            m["cantidad"] if m["tipo"] == "entrada" else -m["cantidad"]
        )
        assert saldo[m["producto_id"]] >= 0
    entradas_compra = sum(m["cantidad"] for m in d["movimientos_stock"] if m["motivo"] == "compra")
    salidas_venta = sum(m["cantidad"] for m in d["movimientos_stock"] if m["motivo"] == "venta")
    assert entradas_compra == sum(c["cantidad"] for c in d["compras"])
    assert salidas_venta == sum(v["cantidad"] for v in d["ventas"])


def test_menos_de_90_dias_es_rechazado():
    with pytest.raises(ValueError):
        generar_datos.generar(dias=60)


# --------------------------------------------------------------------------- #
# 2. Ingesta con dlt
# --------------------------------------------------------------------------- #
@pytest.fixture()
def entorno(tmp_path):
    """CSV generados + rutas temporales para la base y el estado de dlt."""
    data = tmp_path / "data"
    generar_datos.main(["--salida", str(data)])
    return {"data": data, "db": tmp_path / "test.duckdb", "dlt": tmp_path / "dlt_state"}


def _ingestar(env):
    pipeline.ejecutar_ingesta(env["data"], env["db"], pipelines_dir=env["dlt"])


def test_esquema_duckdb_tras_ingesta(entorno):
    _ingestar(entorno)
    con = duckdb.connect(str(entorno["db"]), read_only=True)
    columnas = {
        t: {
            c: tipo
            for c, tipo in con.execute(
                "select column_name, data_type from information_schema.columns "
                "where table_schema = 'raw' and table_name = ?",
                [t],
            ).fetchall()
        }
        for t in TABLAS
    }
    assert set(columnas["ventas"]) >= {
        "id",
        "fecha",
        "producto_id",
        "cantidad",
        "precio_unitario",
        "descuento",
        "vendedor_id",
    }
    assert set(columnas["productos"]) >= {
        "id",
        "nombre",
        "categoria",
        "costo_unitario",
        "precio_venta",
        "stock_inicial",
    }
    assert set(columnas["vendedores"]) >= {"id", "nombre", "sucursal", "fecha_alta"}
    assert set(columnas["compras"]) >= {
        "id",
        "fecha",
        "producto_id",
        "cantidad",
        "costo_unitario",
        "proveedor",
    }
    assert set(columnas["movimientos_stock"]) >= {
        "id",
        "fecha",
        "producto_id",
        "tipo",
        "cantidad",
        "motivo",
        "referencia_id",
    }
    assert columnas["ventas"]["fecha"] == "DATE"
    assert columnas["ventas"]["precio_unitario"] == "DOUBLE"
    assert columnas["ventas"]["cantidad"] == "BIGINT"
    assert pipeline.contar_filas(entorno["db"]) == {
        t: len(generar_datos.generar()[t]) for t in TABLAS
    }
    con.close()


def test_ingesta_es_idempotente(entorno):
    _ingestar(entorno)
    primera = pipeline.contar_filas(entorno["db"])
    _ingestar(entorno)
    _ingestar(entorno)
    assert pipeline.contar_filas(entorno["db"]) == primera
    con = duckdb.connect(str(entorno["db"]), read_only=True)
    for t in TABLAS:
        n, distintos = con.execute(f"select count(*), count(distinct id) from raw.{t}").fetchone()
        assert n == distintos, f"duplicados en raw.{t}"
    con.close()


# --------------------------------------------------------------------------- #
# 3. Integración de punta a punta
# --------------------------------------------------------------------------- #
def test_e2e_generacion_ingesta_dbt_y_reporte(entorno):
    _ingestar(entorno)
    pipeline.ejecutar_dbt(entorno["db"], comando="build")  # incluye las pruebas de dbt

    con = duckdb.connect(str(entorno["db"]), read_only=True)
    marts = {
        r[0]
        for r in con.execute(
            "select table_name from information_schema.tables where table_schema = 'marts'"
        ).fetchall()
    }
    assert marts == {
        "mart_ventas_diarias",
        "mart_rentabilidad_productos",
        "mart_rotacion_inventario",
        "mart_desempeno_vendedores",
        "mart_clasificacion_abc",
    }

    # Conciliación: facturación del mart == facturación recalculada en Python
    # (Decimal) desde los datos origen
    neto_esperado = Decimal("0")
    for v in generar_datos.generar()["ventas"]:
        bruto = (Decimal(str(v["cantidad"])) * Decimal(str(v["precio_unitario"]))).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )
        desc = (bruto * Decimal(str(v["descuento"]))).quantize(Decimal("0.01"), ROUND_HALF_UP)
        neto_esperado += bruto - desc
    neto_mart = con.execute("select sum(ingreso_neto) from marts.mart_ventas_diarias").fetchone()[0]
    assert Decimal(str(neto_mart)) == neto_esperado

    # Rentabilidad: ganancia = ingreso - costo, y los productos suman lo mismo que los días
    assert (
        con.execute(
            "select count(*) from marts.mart_rentabilidad_productos "
            "where abs(ganancia_bruta - (ingreso_neto - costo_ventas)) > 0.01"
        ).fetchone()[0]
        == 0
    )
    g_prod = con.execute(
        "select sum(ganancia_bruta) from marts.mart_rentabilidad_productos"
    ).fetchone()[0]
    g_dia = con.execute("select sum(ganancia_bruta) from marts.mart_ventas_diarias").fetchone()[0]
    assert float(g_prod) == pytest.approx(float(g_dia), abs=0.01)

    # ABC: A + B + C = 20 productos, acumulado termina en 100 %
    abc = dict(
        con.execute(
            "select clasificacion_abc, count(*) from marts.mart_clasificacion_abc group by 1"
        ).fetchall()
    )
    assert sum(abc.values()) == 20 and {"A", "B", "C"} >= set(abc)
    assert float(
        con.execute(
            "select max(participacion_acumulada_pct) from marts.mart_clasificacion_abc"
        ).fetchone()[0]
    ) == pytest.approx(100, abs=0.1)

    # Vendedores: el ranking 1 es el de mayor ingreso
    top = con.execute(
        "select nombre_vendedor from marts.mart_desempeno_vendedores where ranking = 1"
    ).fetchone()[0]
    mejor = con.execute(
        "select nombre_vendedor from marts.mart_desempeno_vendedores "
        "order by ingreso_neto desc limit 1"
    ).fetchone()[0]
    assert top == mejor
    con.close()

    reporte = analisis.generar_reporte_calidad(entorno["db"])
    fallidos = [c for c in reporte["checks"] if not c["ok"]]
    assert reporte["ok"], f"Validaciones fallidas: {fallidos}"
