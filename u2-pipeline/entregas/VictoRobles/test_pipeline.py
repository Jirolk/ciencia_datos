"""Pruebas del pipeline de Open-Meteo: simulan la API, no usan internet."""

import pipeline
import pytest
import requests

DATOS_FALSOS = {
    "latitude": -25.27,
    "longitude": -57.6,
    "hourly": {
        "time": ["2026-10-23T00:00", "2026-10-23T01:00"],
        "temperature_2m": [22.6, 22.4],
        "precipitation": [0, 7.9],
    },
}


class RespuestaFalsa:
    """Imita la respuesta que daría la API."""

    def __init__(self, datos):
        self._datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self._datos


def test_filas_por_hora_convierte_listas_en_filas():
    filas = pipeline.filas_por_hora(DATOS_FALSOS)
    assert len(filas) == 2
    assert filas[1] == {
        "time": "2026-10-23T01:00",
        "temperature_2m": 22.4,
        "precipitation": 7.9,
        "latitude": -25.27,
        "longitude": -57.6,
    }


def test_recurso_entrega_una_fila_por_hora(monkeypatch):
    monkeypatch.setattr(
        pipeline.requests,
        "get",
        lambda url, params=None, timeout=None: RespuestaFalsa(DATOS_FALSOS),
    )
    filas = list(pipeline.pronostico_horario())
    assert len(filas) == 2


def test_respuesta_vacia_no_genera_filas():
    assert pipeline.filas_por_hora({}) == []
    assert pipeline.filas_por_hora({"hourly": {}}) == []


def test_error_de_conexion_se_propaga(monkeypatch):
    def falla(url, params=None, timeout=None):
        raise requests.ConnectionError("sin internet")

    monkeypatch.setattr(pipeline.requests, "get", falla)
    with pytest.raises(requests.ConnectionError):
        pipeline.pedir_pronostico()
