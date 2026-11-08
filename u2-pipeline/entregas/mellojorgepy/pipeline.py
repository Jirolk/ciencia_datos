"""Pipeline U2: Rick and Morty API -> dlt -> DuckDB (data.duckdb).

Extrae todos los personajes de la API pública (paginada), valida que cada
registro traiga los campos obligatorios, los aplana en una tabla limpia y
los carga en DuckDB bajo el esquema ``rick_and_morty``.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
from dlt.sources.helpers import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

URL_PERSONAJES = "https://rickandmortyapi.com/api/character"
RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"
NOMBRE_ESQUEMA = "rick_and_morty"
CAMPOS_OBLIGATORIOS = ("id", "name", "status", "species", "gender")

# Esquema explícito: dlt infiere tipos, pero una columna que llega siempre
# vacía (p. ej. "tipo") no se materializa si no se le declara el tipo.
COLUMNAS = {
    "id": {"data_type": "bigint", "nullable": False},
    "nombre": {"data_type": "text", "nullable": False},
    "estado": {"data_type": "text"},
    "especie": {"data_type": "text"},
    "tipo": {"data_type": "text"},
    "genero": {"data_type": "text"},
    "origen": {"data_type": "text"},
    "ubicacion": {"data_type": "text"},
    "n_episodios": {"data_type": "bigint"},
    "creado": {"data_type": "timestamp"},
}


def descargar_pagina(url: str) -> dict[str, Any]:
    """Descarga una página de la API.

    La API responde 404 cuando no hay resultados; lo tratamos como una
    página vacía en lugar de un error. Cualquier otro fallo se propaga.
    """
    try:
        respuesta = requests.get(url, timeout=30)
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            logger.warning("La API no devolvió resultados para %s", url)
            return {"info": {"next": None}, "results": []}
        raise
    return respuesta.json()


def iterar_paginas(url: str = URL_PERSONAJES) -> Iterator[list[dict[str, Any]]]:
    """Recorre la paginación siguiendo el campo ``info.next``."""
    siguiente: str | None = url
    while siguiente:
        datos = descargar_pagina(siguiente)
        yield datos.get("results") or []
        siguiente = (datos.get("info") or {}).get("next")


def limpiar_personaje(crudo: dict[str, Any]) -> dict[str, Any]:
    """Valida los campos obligatorios y aplana el registro.

    ``origin`` y ``location`` son objetos anidados y ``episode`` es una
    lista: dlt los convertiría en columnas con ``__`` y en una tabla hija.
    Aquí se reducen a columnas simples para obtener una tabla limpia.
    """
    faltantes = [c for c in CAMPOS_OBLIGATORIOS if crudo.get(c) in (None, "")]
    if faltantes:
        raise ValueError(f"Registro {crudo.get('id')} sin campos: {faltantes}")

    return {
        "id": int(crudo["id"]),
        "nombre": crudo["name"].strip(),
        "estado": crudo["status"],
        "especie": crudo["species"],
        "tipo": crudo.get("type") or None,
        "genero": crudo["gender"],
        "origen": (crudo.get("origin") or {}).get("name"),
        "ubicacion": (crudo.get("location") or {}).get("name"),
        "n_episodios": len(crudo.get("episode") or []),
        "creado": crudo.get("created"),
    }


@dlt.resource(
    name="personajes",
    primary_key="id",
    write_disposition="replace",
    columns=COLUMNAS,
)
def personajes(url: str = URL_PERSONAJES) -> Iterator[list[dict[str, Any]]]:
    """Recurso dlt: entrega los personajes página a página."""
    total = 0
    for pagina in iterar_paginas(url):
        filas = [limpiar_personaje(p) for p in pagina]
        total += len(filas)
        if filas:
            yield filas
    logger.info("personajes: %d registros extraídos", total)


def construir_pipeline(ruta_db: Path = RUTA_DB) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="u2_rick_and_morty",
        destination=dlt.destinations.duckdb(str(ruta_db)),
        dataset_name=NOMBRE_ESQUEMA,
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(personajes())
    print(info)
    print(f"Base de datos: {RUTA_DB}")


if __name__ == "__main__":
    main()
