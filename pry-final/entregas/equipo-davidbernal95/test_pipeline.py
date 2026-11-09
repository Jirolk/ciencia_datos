"""Pruebas de reproducibilidad, carga idempotente y flujo completo."""

import csv
import json
from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import duckdb
import pytest

from configuracion import TABLAS
from generar_datos import generar_datos
from orchestration.definitions import defs
from pipeline import ejecutar_ingesta, leer_csv


def filas(carpeta, nombre):
    with (carpeta / f"{nombre}.csv").open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def test_generacion_reproducible_y_consistente(tmp_path):
    a, b, c = (tmp_path / nombre for nombre in ("a", "b", "c"))
    cantidades = generar_datos(a)
    assert cantidades == generar_datos(b)
    generar_datos(c, seed=2027)
    assert all((a / f"{t}.csv").read_bytes() == (b / f"{t}.csv").read_bytes() for t in TABLAS)
    assert (a / "ventas.csv").read_bytes() != (c / "ventas.csv").read_bytes()

    productos = filas(a, "productos")
    compras = filas(a, "compras")
    ventas = filas(a, "ventas")
    vendedores = filas(a, "vendedores")
    fechas = {date.fromisoformat(v["fecha"]) for v in ventas}
    assert len(fechas) == 90 and (max(fechas) - min(fechas)).days == 89
    assert len(productos) == 20 and len(vendedores) == 5
    assert len(compras) >= 100 and len(ventas) >= 500
    assert {v["vendedor_id"] for v in ventas} <= {v["id"] for v in vendedores}
    saldo = {p["id"]: int(p["stock_inicial"]) for p in productos}
    for mov in filas(a, "movimientos_stock"):
        delta = int(mov["cantidad"])
        saldo[mov["producto_id"]] += delta if mov["tipo"] == "entrada" else -delta
        assert saldo[mov["producto_id"]] >= 0


def test_ingesta_crea_esquema_y_no_duplica(tmp_path):
    datos = tmp_path / "data"
    esperados = generar_datos(datos)
    base = tmp_path / "data.duckdb"

    for _ in range(2):
        ejecutar_ingesta(datos, base)
        with duckdb.connect(str(base), read_only=True) as conexion:
            for tabla, cantidad in esperados.items():
                filas_cargadas = conexion.execute(
                    f"select count(*), count(distinct id) from raw_minimercado.{tabla}"
                ).fetchone()
                assert filas_cargadas == (cantidad, cantidad)
            columnas = dict(
                conexion.execute("""
                    select column_name, data_type
                    from information_schema.columns
                    where table_schema = 'raw_minimercado' and table_name = 'ventas'
                """).fetchall()
            )
            assert columnas["fecha"] == "DATE"
            assert columnas["producto_id"] == "BIGINT"
            assert columnas["precio_unitario"].startswith("DECIMAL")


def test_ingesta_rechaza_snapshot_incompleto(tmp_path):
    (tmp_path / "ventas.csv").write_text(
        "id,fecha,producto_id,cantidad,precio_unitario,descuento,vendedor_id\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="está vacío"):
        leer_csv(tmp_path, "ventas")


def test_flujo_completo_y_metricas_independientes(tmp_path, monkeypatch):
    monkeypatch.setenv("MINIMERCADO_WORKDIR", str(tmp_path))
    corrida = defs.resolve_job_def("minimercado_job").execute_in_process()
    assert corrida.success
    assert len(corrida.get_asset_materialization_events()) == 4
    resultado = json.loads(
        (tmp_path / ".runtime" / "reporte_calidad.json").read_text(encoding="utf-8")
    )
    assert resultado["controles"] == "aprobados"

    carpeta = tmp_path / "data"
    productos = filas(carpeta, "productos")
    compras = filas(carpeta, "compras")
    ventas = filas(carpeta, "ventas")
    total, unidades = Decimal("0"), 0
    importe_producto = defaultdict(Decimal)
    importe_diario = defaultdict(Decimal)
    lineas_diarias = defaultdict(int)
    unidades_producto = defaultdict(int)
    saldo = {p["id"]: int(p["stock_inicial"]) for p in productos}
    costos = {p["id"]: saldo[p["id"]] * Decimal(p["costo_unitario"]) for p in productos}

    for c in compras:
        cantidad = int(c["cantidad"])
        saldo[c["producto_id"]] += cantidad
        costos[c["producto_id"]] += cantidad * Decimal(c["costo_unitario"])
    disponibles = saldo.copy()

    for v in ventas:
        cantidad = int(v["cantidad"])
        id_ = v["producto_id"]
        neto = (cantidad * Decimal(v["precio_unitario"]) * (1 - Decimal(v["descuento"]))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total += neto
        importe_diario[v["fecha"]] += neto
        lineas_diarias[v["fecha"]] += 1
        unidades += cantidad
        importe_producto[id_] += neto
        unidades_producto[id_] += cantidad
        saldo[id_] -= cantidad

    estadistica = resultado["01_estadistica"][0]
    assert estadistica["dias"] == 90
    assert Decimal(estadistica["facturacion_total"]) == total
    assert estadistica["unidades_vendidas"] == unidades
    assert estadistica["lineas_venta"] == len(ventas)
    assert Decimal(str(estadistica["importe_promedio_linea"])) == (total / len(ventas)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert sum(row["unidades"] for row in resultado["04_abc"]) == unidades
    assert sum(Decimal(row["facturacion_neta"]) for row in resultado["03_vendedores"]) == total

    with duckdb.connect(str(tmp_path / "data.duckdb"), read_only=True) as conexion:
        promedios = conexion.execute("""
            select fecha, lineas_venta, importe_promedio_linea
            from analitica.mart_ventas_diarias order by fecha
        """).fetchall()
        for fecha, cantidad_lineas, promedio in promedios:
            clave_fecha = fecha.isoformat()
            assert cantidad_lineas == lineas_diarias[clave_fecha]
            esperado = (importe_diario[clave_fecha] / lineas_diarias[clave_fecha]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            assert Decimal(str(promedio)) == esperado
        assert conexion.execute("select count(*) from analitica.fct_ventas").fetchone()[0] == len(
            ventas
        )
        assert conexion.execute("select count(*) from analitica.fct_compras").fetchone()[0] == len(
            compras
        )
        assert conexion.execute("select count(*) from analitica.dim_productos").fetchone()[0] == 20
        assert conexion.execute("select count(*) from analitica.dim_vendedores").fetchone()[0] == 5
        assert conexion.execute("select count(*) from analitica.dim_fecha").fetchone()[0] == 90
        unidos = conexion.execute("""
            select count(*), sum(f.importe_neto)
            from analitica.fct_ventas f
            join analitica.dim_productos p using (producto_id)
            join analitica.dim_vendedores v using (vendedor_id)
            join analitica.dim_fecha d using (fecha)
        """).fetchone()
        assert unidos == (len(ventas), total)
        saldos = conexion.execute("""
            select producto_id, stock_actual from analitica.mart_rotacion_inventario
        """).fetchall()
        assert {str(id_): valor for id_, valor in saldos} == saldo
        ganancias = conexion.execute("""
            select producto_id, ganancia_bruta from analitica.mart_rentabilidad_productos
        """).fetchall()
        for id_, ganancia in ganancias:
            clave = str(id_)
            costo = (costos[clave] * unidades_producto[clave] / disponibles[clave]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            assert ganancia == importe_producto[clave] - costo
