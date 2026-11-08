"""Pruebas del pipeline. No usan internet: reemplazan pedir_cotizaciones por datos falsos."""

import duckdb
import pipeline
import pytest
import requests
from dlt.extract.exceptions import ResourceExtractionError


def cotizacion(fecha: str, moneda: str, tasa: float) -> dict:
    return {"date": fecha, "base": "USD", "quote": moneda, "rate": tasa}


class ApiFalsa:
    """Imita a la API: devuelve los registros con fecha >= desde y anota cada pedido."""

    def __init__(self, registros: list[dict]):
        self.registros = registros
        self.pedidos: list[str] = []

    def __call__(self, desde: str) -> list[dict]:
        self.pedidos.append(desde)
        return [r for r in self.registros if r["date"] >= desde]


def contar_filas(ruta_db) -> int:
    with duckdb.connect(str(ruta_db), read_only=True) as con:
        return con.execute("SELECT COUNT(*) FROM tipo_cambio.cotizaciones").fetchone()[0]


def test_carga_cotizaciones_con_la_estructura_esperada(monkeypatch, tmp_path):
    api = ApiFalsa(
        [
            cotizacion("2026-10-01", "PYG", 5850.69),
            cotizacion("2026-10-01", "BRL", 5.2167),
            cotizacion("2026-10-02", "PYG", 5873.69),
            cotizacion("2026-10-02", "BRL", 5.2308),
        ]
    )
    monkeypatch.setattr(pipeline, "pedir_cotizaciones", api)

    ruta_db = tmp_path / "prueba.duckdb"
    p = pipeline.construir_pipeline(ruta_db=ruta_db, pipelines_dir=str(tmp_path / "estado"))
    p.run(pipeline.tipo_cambio_source())

    with duckdb.connect(str(ruta_db), read_only=True) as con:
        filas = con.execute("DESCRIBE tipo_cambio.cotizaciones").fetchall()
    tipos = {nombre: tipo for nombre, tipo, *_ in filas}  # columna -> tipo SQL

    assert {"date", "base", "quote", "rate"} <= tipos.keys()
    assert tipos["date"] == "DATE"
    assert tipos["rate"] == "DOUBLE"
    assert contar_filas(ruta_db) == 4
    assert api.pedidos == [pipeline.FECHA_INICIAL]  # la primera corrida arranca desde el inicio


def test_segunda_corrida_es_incremental_y_no_duplica(monkeypatch, tmp_path):
    api = ApiFalsa(
        [cotizacion("2026-10-01", "PYG", 5850.69), cotizacion("2026-10-02", "PYG", 5873.69)]
    )
    monkeypatch.setattr(pipeline, "pedir_cotizaciones", api)

    ruta_db = tmp_path / "prueba.duckdb"
    p = pipeline.construir_pipeline(ruta_db=ruta_db, pipelines_dir=str(tmp_path / "estado"))
    p.run(pipeline.tipo_cambio_source())

    # Al dia siguiente la API publica una cotizacion nueva.
    api.registros.append(cotizacion("2026-10-05", "PYG", 5864.90))
    p.run(pipeline.tipo_cambio_source())

    assert api.pedidos[1] == "2026-10-02"  # pidio desde la ultima fecha cargada
    assert contar_filas(ruta_db) == 3  # 2 + 1 nueva, sin repetir el 2026-10-02


def test_respuesta_vacia_no_produce_filas(monkeypatch):
    monkeypatch.setattr(pipeline, "pedir_cotizaciones", lambda desde: [])

    assert list(pipeline.cotizaciones()) == []


def test_error_de_conexion_no_se_oculta(monkeypatch):
    def sin_conexion(desde):
        raise requests.ConnectionError("API caida")

    monkeypatch.setattr(pipeline, "pedir_cotizaciones", sin_conexion)

    # dlt envuelve el error en ResourceExtractionError; la causa original se conserva.
    with pytest.raises(ResourceExtractionError) as error:
        list(pipeline.cotizaciones())

    assert isinstance(error.value.__cause__, requests.ConnectionError)
