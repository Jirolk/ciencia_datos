"""Pruebas sin llamadas a internet y con bases temporales."""

import duckdb
import pipeline
import pytest
from requests.exceptions import ConnectionError, HTTPError
from verificar_datos import verificar_datos


class RespuestaSimulada:
    def __init__(self, datos, error_http=None):
        self.datos = datos
        self.error_http = error_http

    def raise_for_status(self):
        if self.error_http is not None:
            raise self.error_http

    def json(self):
        return self.datos


@pytest.fixture
def publicaciones():
    return [
        {"id": 1, "userId": 1, "title": "Primera", "body": "Contenido uno"},
        {"id": 2, "userId": 1, "title": "Segunda", "body": "Contenido dos"},
    ]


def simular_respuesta(monkeypatch, datos):
    def get_simulado(url, timeout):
        assert url == pipeline.API_URL
        assert timeout == 30
        return RespuestaSimulada(datos)

    monkeypatch.setattr(pipeline.requests, "get", get_simulado)


def test_recurso_dlt_obtiene_la_estructura_esperada(monkeypatch, publicaciones):
    simular_respuesta(monkeypatch, publicaciones)
    recurso = pipeline.extraer_posts()

    assert recurso.name == "posts"
    assert recurso.write_disposition == "replace"
    assert list(recurso) == publicaciones


def test_respuesta_vacia_cancela_la_carga(monkeypatch):
    simular_respuesta(monkeypatch, [])

    with pytest.raises(ValueError, match="lista vacía"):
        pipeline.obtener_posts()


@pytest.mark.parametrize(
    "datos",
    [
        {"mensaje": "esto no es una lista"},
        ["esto no es una publicación"],
        [{"id": 1, "userId": 1, "title": "Falta body"}],
        [{"id": "uno", "userId": 1, "title": "Título", "body": "Cuerpo"}],
        [{"id": 1, "userId": 1, "title": None, "body": "Cuerpo"}],
    ],
)
def test_rechaza_estructuras_y_tipos_invalidos(monkeypatch, datos):
    simular_respuesta(monkeypatch, datos)

    with pytest.raises(ValueError):
        pipeline.obtener_posts()


def test_error_de_conexion_se_propaga(monkeypatch):
    def get_con_error(url, timeout):
        raise ConnectionError("Conexión simulada interrumpida")

    monkeypatch.setattr(pipeline.requests, "get", get_con_error)

    with pytest.raises(ConnectionError, match="simulada"):
        pipeline.obtener_posts()


def test_error_http_no_se_interpreta_como_datos(monkeypatch):
    def get_con_error_http(url, timeout):
        return RespuestaSimulada([], HTTPError("HTTP 503 simulado"))

    monkeypatch.setattr(pipeline.requests, "get", get_con_error_http)

    with pytest.raises(HTTPError, match="503"):
        pipeline.obtener_posts()


def test_carga_persistente_y_repetible(monkeypatch, tmp_path, publicaciones):
    simular_respuesta(monkeypatch, publicaciones)
    ruta_db = tmp_path / "data.duckdb"
    estado = tmp_path / "estado_dlt"

    pipeline.ejecutar_pipeline(ruta_db, estado)
    assert ruta_db.is_file()
    assert verificar_datos(ruta_db)["total"] == 2

    pipeline.ejecutar_pipeline(ruta_db, estado)
    resultados = verificar_datos(ruta_db)
    assert resultados["total"] == 2
    assert resultados["por_usuario"] == [(1, 2)]
    assert {"id", "user_id", "title", "body"}.issubset(
        {columna[0] for columna in resultados["columnas"]}
    )
    with duckdb.connect(str(ruta_db), read_only=True) as conexion:
        assert conexion.execute("SELECT id FROM jsonplaceholder.posts ORDER BY id").fetchall() == [
            (1,),
            (2,),
        ]


def test_verificacion_no_crea_una_base_inexistente(tmp_path):
    ruta_db = tmp_path / "inexistente.duckdb"

    with pytest.raises(FileNotFoundError, match="primero pipeline.py"):
        verificar_datos(ruta_db)

    assert not ruta_db.exists()
