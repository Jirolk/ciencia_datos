"""Pruebas del pipeline: no usan internet, simulan la respuesta de la API."""

import pipeline
import pytest
import requests

POSTS_FALSOS = [
    {"userId": 1, "id": 1, "title": "uno", "body": "texto uno"},
    {"userId": 1, "id": 2, "title": "dos", "body": "texto dos"},
]


class RespuestaFalsa:
    """Imita la respuesta que daría la API."""

    def __init__(self, datos):
        self._datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self._datos


def test_recurso_devuelve_posts_con_estructura_esperada(monkeypatch):
    monkeypatch.setattr(
        pipeline.requests, "get", lambda url, timeout=None: RespuestaFalsa(POSTS_FALSOS)
    )
    filas = list(pipeline.posts())
    assert len(filas) == 2
    assert {"userId", "id", "title", "body"} <= set(filas[0])


def test_respuesta_vacia_no_genera_filas(monkeypatch):
    monkeypatch.setattr(pipeline.requests, "get", lambda url, timeout=None: RespuestaFalsa([]))
    assert list(pipeline.posts()) == []


def test_error_de_conexion_se_propaga(monkeypatch):
    def falla(url, timeout=None):
        raise requests.ConnectionError("sin internet")

    monkeypatch.setattr(pipeline.requests, "get", falla)
    with pytest.raises(requests.ConnectionError):
        pipeline.obtener_posts()
