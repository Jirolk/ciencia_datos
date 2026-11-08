"""Pruebas de la tarea U2 para el pipeline de JSONPlaceholder."""

from __future__ import annotations

import pytest
from pipeline import obtener_posts, posts

POST_DE_EJEMPLO = {"id": 1, "title": "prueba", "body": "contenido", "userId": 1}


def test_recurso_dlt_entrega_estructura_esperada():
    """El recurso cede los dicts tal cual, con las claves que trae la API."""
    filas = list(posts(filas=[POST_DE_EJEMPLO, {**POST_DE_EJEMPLO, "id": 2}]))
    assert len(filas) == 2
    assert all({"id", "title", "body", "userId"} <= set(fila) for fila in filas)


def test_recurso_respuesta_vacia_no_lanza_error():
    """Caso borde: lista vacía -> no truena y no cede ninguna fila."""
    assert list(posts(filas=[])) == []


def test_obtener_posts_rechaza_respuesta_invalida(monkeypatch):
    """Caso borde: si la API devuelve algo que no es lista, falla con mensaje claro."""

    class RespuestaFalsa:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json() -> dict:
            return {"error": "no encontrado"}

    monkeypatch.setattr("pipeline.requests.get", lambda *args, **kwargs: RespuestaFalsa())
    with pytest.raises(ValueError, match="lista de posts"):
        obtener_posts()
