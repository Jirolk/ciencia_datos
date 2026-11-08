"""Pruebas del pipeline dlt, sin llamar a la API real."""

from unittest.mock import MagicMock, patch

import pipeline
import pytest
from dlt.extract.exceptions import ResourceExtractionError

USUARIOS = [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Luis"}]


def respuesta_falsa(datos):
    """Crea una respuesta simulada de la API que devuelve 'datos'."""
    respuesta = MagicMock()
    respuesta.json.return_value = datos
    return respuesta


def filas(recurso):
    """Junta todas las filas que entrega un recurso dlt en una sola lista."""
    resultado = []
    for item in recurso:
        resultado.extend(item if isinstance(item, list) else [item])
    return resultado


def test_recurso_entrega_las_filas_de_la_api():
    falsa = respuesta_falsa(USUARIOS)
    with patch.object(pipeline.requests, "get", return_value=falsa):
        recurso = pipeline.users()
        assert recurso.name == "users"
        assert filas(recurso) == USUARIOS


def test_respuesta_vacia_no_genera_filas():
    falsa = respuesta_falsa([])
    with patch.object(pipeline.requests, "get", return_value=falsa):
        assert filas(pipeline.users()) == []


def test_error_de_conexion_se_informa_como_error_de_extraccion():
    error = ConnectionError("sin red")
    with patch.object(pipeline.requests, "get", side_effect=error):
        with pytest.raises(ResourceExtractionError, match="sin red"):
            filas(pipeline.users())
