from unittest.mock import Mock

import duckdb
import pipeline
import pytest
import requests
from dlt.extract.exceptions import ResourceExtractionError

USUARIO = {
    "id": 1,
    "name": "Ana Torres",
    "address": {"city": "Encarnación", "geo": {"lat": "-27.33", "lng": "-55.86"}},
    "company": {"name": "Yerba Sur", "catchPhrase": "Siempre fresca"},
}
TAREA = {"userId": 1, "id": 7, "title": "estudiar dlt", "completed": True}


def api_falsa(monkeypatch, usuarios: list, tareas: list) -> None:
    """Reemplaza requests.get: devuelve usuarios o tareas según la URL pedida."""

    def get_falso(url, timeout):
        respuesta = Mock()
        respuesta.json.return_value = usuarios if url.endswith("/users") else tareas
        return respuesta

    monkeypatch.setattr(pipeline.requests, "get", get_falso)


def test_recursos_entregan_los_registros_de_la_api(monkeypatch):
    """Cada recurso dlt devuelve los registros tal como llegan del endpoint."""
    api_falsa(monkeypatch, [USUARIO], [TAREA])

    assert list(pipeline.usuarios()) == [USUARIO]
    assert list(pipeline.tareas()) == [TAREA]


def test_carga_en_duckdb_con_esquema_aplanado(monkeypatch, tmp_path):
    """dlt guarda las dos tablas y convierte lo anidado en columnas planas."""
    api_falsa(monkeypatch, [USUARIO], [TAREA])
    monkeypatch.setenv("DLT_DATA_DIR", str(tmp_path / ".dlt"))
    ruta_bd = tmp_path / "data.duckdb"

    pipeline.construir_pipeline(ruta_bd).run(pipeline.jsonplaceholder())

    with duckdb.connect(str(ruta_bd), read_only=True) as conexion:
        ciudad = conexion.execute("SELECT address__city FROM jsonplaceholder.usuarios").fetchone()
        tarea = conexion.execute("SELECT user_id, completed FROM jsonplaceholder.tareas").fetchone()
    assert ciudad == ("Encarnación",)
    assert tarea == (1, True)


def test_respuesta_vacia_no_crea_registros(monkeypatch):
    """Caso borde: si la API devuelve listas vacías, no aparecen filas inventadas."""
    api_falsa(monkeypatch, [], [])

    assert list(pipeline.usuarios()) == []
    assert list(pipeline.tareas()) == []


def test_error_de_conexion_detiene_la_extraccion(monkeypatch):
    """Caso borde: sin conexión, dlt detiene la extracción e informa el error original."""

    def sin_conexion(url, timeout):
        raise requests.ConnectionError("Sin internet")

    monkeypatch.setattr(pipeline.requests, "get", sin_conexion)

    with pytest.raises(ResourceExtractionError, match="Sin internet"):
        list(pipeline.usuarios())
