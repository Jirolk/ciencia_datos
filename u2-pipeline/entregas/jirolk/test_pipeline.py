from unittest.mock import patch

import pytest
from pipeline import obtener_publicaciones, recurso_publicaciones


def test_recurso_preserva_estructura_de_publicacion():
    publicaciones = [{"userId": 1, "id": 1, "title": "Hola", "body": "Contenido"}]

    with patch("pipeline.obtener_publicaciones", return_value=publicaciones):
        resultado = list(recurso_publicaciones())

    assert resultado == publicaciones
    assert resultado[0]["userId"] == 1
    assert {"id", "title", "body"}.issubset(resultado[0])


def test_recurso_permite_respuesta_vacia():
    resultado = list(recurso_publicaciones([]))
    assert resultado == []


def test_error_de_conexion_se_convierte_en_mensaje_claro():
    from urllib.error import URLError

    with patch("pipeline.urlopen", side_effect=URLError("sin red")):
        with pytest.raises(RuntimeError, match="No fue posible conectar"):
            obtener_publicaciones()
