"""Pruebas unitarias para el pipeline de dlt y el recurso de extracción."""

import dlt.extract.exceptions
import pytest
import requests
from pipeline import obtener_usuarios


def test_obtener_usuarios_estructura_correcta():
    """Prueba que el recurso dlt extrae datos y los registros contienen campos esperados."""
    usuarios = list(obtener_usuarios())

    assert len(usuarios) > 0, "La lista de usuarios extraída no debe estar vacía"
    primer_usuario = usuarios[0]
    assert "id" in primer_usuario, "El registro debe contener la clave 'id'"
    assert "name" in primer_usuario, "El registro debe contener la clave 'name'"
    assert "email" in primer_usuario, "El registro debe contener la clave 'email'"


def test_obtener_usuarios_caso_borde_url_invalida():
    """Caso borde: simular error cuando la URL es inexistente o genera error HTTP."""
    url_erronea = "https://jsonplaceholder.typicode.com/recurso_inexistente_404"

    # dlt captura el error HTTP de la función interna y lanza ResourceExtractionError
    with pytest.raises(
        (
            requests.exceptions.HTTPError,
            dlt.extract.exceptions.ResourceExtractionError,
        )
    ):
        list(obtener_usuarios(url=url_erronea))


def test_obtener_usuarios_caso_borde_lista_vacia(monkeypatch):
    """Caso borde: validar que si la API responde lista vacía, el recurso retorna 0."""

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    # Simulamos una respuesta con 0 datos sin hacer llamada a internet
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())

    resultado = list(obtener_usuarios())
    assert resultado == [], "Si la API no trae datos, el recurso debe arrojar una lista vacía"
