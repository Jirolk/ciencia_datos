"""Pruebas con respuestas simuladas: no dependen de que la API esté disponible."""

import duckdb
import pytest
from dlt.extract.exceptions import ResourceExtractionError
from pipeline import URL_API, construir_pipeline, publicaciones
from requests.exceptions import ConnectionError as ErrorConexion

DATOS = [
    {"userId": 1, "id": 1, "title": "Primera publicación", "body": "Texto de prueba"},
    {"userId": 2, "id": 2, "title": "Segunda publicación", "body": "Otro texto"},
]


class RespuestaSimulada:
    def __init__(self, datos):
        self.datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self.datos


def simular_respuesta(monkeypatch, datos):
    def obtener(url, timeout):
        assert url == URL_API
        assert timeout == 30
        return RespuestaSimulada(datos)

    monkeypatch.setattr("pipeline.requests.get", obtener)


def test_recurso_entrega_los_registros_esperados(monkeypatch):
    simular_respuesta(monkeypatch, DATOS)
    assert publicaciones().name == "publicaciones"
    assert list(publicaciones()) == DATOS


@pytest.mark.parametrize("datos", [[], {}, [{"id": 1}]])
def test_rechaza_respuestas_vacias_o_incompletas(monkeypatch, datos):
    simular_respuesta(monkeypatch, datos)
    with pytest.raises(ResourceExtractionError) as error:
        list(publicaciones())
    assert isinstance(error.value.__cause__, ValueError)


def test_informa_un_error_de_conexion(monkeypatch):
    def fallar(url, timeout):
        raise ErrorConexion("Sin conexión a la API")

    monkeypatch.setattr("pipeline.requests.get", fallar)
    with pytest.raises(ResourceExtractionError, match="Sin conexión") as error:
        list(publicaciones())
    assert isinstance(error.value.__cause__, ErrorConexion)


def test_carga_persistente_y_sin_duplicados(monkeypatch, tmp_path):
    simular_respuesta(monkeypatch, DATOS)
    ruta_db = tmp_path / "data.duckdb"
    pipeline = construir_pipeline(ruta_db)
    pipeline.run(publicaciones())
    pipeline.run(publicaciones())

    assert ruta_db.is_file()
    with duckdb.connect(str(ruta_db), read_only=True) as conexion:
        registros = conexion.execute(
            "SELECT id, user_id, title, body FROM api_publica.publicaciones ORDER BY id"
        ).fetchall()
    assert registros == [
        (1, 1, "Primera publicación", "Texto de prueba"),
        (2, 2, "Segunda publicación", "Otro texto"),
    ]
