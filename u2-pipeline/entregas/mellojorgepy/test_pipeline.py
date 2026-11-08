"""Pruebas del pipeline U2. No usan la red: las respuestas de la API se simulan."""

from __future__ import annotations

from unittest.mock import Mock

import duckdb
import pipeline
import pytest
from dlt.sources.helpers import requests

URL = pipeline.URL_PERSONAJES


def personaje(id_: int, **cambios) -> dict:
    base = {
        "id": id_,
        "name": f"  Personaje {id_} ",
        "status": "Alive",
        "species": "Human",
        "type": "",
        "gender": "Male",
        "origin": {"name": "Earth (C-137)", "url": ""},
        "location": {"name": "Citadel of Ricks", "url": ""},
        "episode": ["ep/1", "ep/2"],
        "created": "2017-11-04T18:48:46.250Z",
    }
    base.update(cambios)
    return base


@pytest.fixture
def api_dos_paginas(monkeypatch):
    """Simula una API con dos páginas de resultados."""
    paginas = {
        URL: {"info": {"next": f"{URL}?page=2"}, "results": [personaje(1)]},
        f"{URL}?page=2": {"info": {"next": None}, "results": [personaje(2)]},
    }
    monkeypatch.setattr(pipeline, "descargar_pagina", lambda url: paginas[url])


def test_recurso_estructura_y_paginacion(api_dos_paginas):
    filas = list(pipeline.personajes())

    assert [f["id"] for f in filas] == [1, 2]  # recorrió ambas páginas
    assert set(filas[0]) == {
        "id",
        "nombre",
        "estado",
        "especie",
        "tipo",
        "genero",
        "origen",
        "ubicacion",
        "n_episodios",
        "creado",
    }
    assert filas[0]["nombre"] == "Personaje 1"  # espacios recortados
    assert filas[0]["origen"] == "Earth (C-137)"  # objeto anidado aplanado
    assert filas[0]["n_episodios"] == 2
    assert filas[0]["tipo"] is None  # cadena vacía -> NULL


def test_respuesta_vacia_no_genera_filas(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "descargar_pagina",
        lambda url: {"info": {"next": None}, "results": []},
    )
    assert list(pipeline.personajes()) == []


def test_404_de_la_api_se_trata_como_vacio(monkeypatch):
    error = requests.HTTPError(response=Mock(status_code=404))
    monkeypatch.setattr(pipeline.requests, "get", Mock(side_effect=error))

    assert pipeline.descargar_pagina(URL) == {"info": {"next": None}, "results": []}


def test_error_de_conexion_se_propaga(monkeypatch):
    monkeypatch.setattr(
        pipeline.requests,
        "get",
        Mock(side_effect=requests.ConnectionError("sin red")),
    )
    with pytest.raises(requests.ConnectionError):
        list(pipeline.iterar_paginas())


def test_registro_sin_campo_obligatorio_falla():
    with pytest.raises(ValueError, match="name"):
        pipeline.limpiar_personaje(personaje(3, name=None))


def test_carga_en_duckdb(api_dos_paginas, tmp_path):
    ruta_db = tmp_path / "data.duckdb"
    pipeline.construir_pipeline(ruta_db).run(pipeline.personajes())

    with duckdb.connect(str(ruta_db), read_only=True) as con:
        total = con.execute("SELECT COUNT(*) FROM rick_and_morty.personajes").fetchone()[0]
    assert total == 2
