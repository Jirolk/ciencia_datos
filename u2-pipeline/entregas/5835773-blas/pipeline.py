"""Pipeline de la tarea U2: ingesta de posts de JSONPlaceholder a DuckDB con dlt."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import dlt
import requests

URL_API = "https://jsonplaceholder.typicode.com/posts"
RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"
TIEMPO_ESPERA = 30


def obtener_posts(url: str = URL_API) -> list[dict]:
    """Descarga los posts desde la API y devuelve una lista de dicts."""
    respuesta = requests.get(url, timeout=TIEMPO_ESPERA)
    respuesta.raise_for_status()
    datos = respuesta.json()
    if not isinstance(datos, list):
        raise ValueError(f"Se esperaba una lista de posts, llegó {type(datos).__name__}")
    return datos


@dlt.resource(name="posts", write_disposition="merge", primary_key="id")
def posts(filas: list[dict] | None = None) -> Iterator[dict]:
    """Recurso de dlt que cede los posts uno a uno.

    Si se pasan filas, no consulta la API: así los tests corren sin red.
    """
    if filas is None:
        filas = obtener_posts()
    yield from filas


def construir_pipeline() -> dlt.Pipeline:
    """Crea el pipeline que escribe en data.duckdb bajo el esquema u2_posts."""
    return dlt.pipeline(
        pipeline_name="u2_posts",
        destination=dlt.destinations.duckdb(credentials="duckdb:///" + RUTA_DB.as_posix()),
        dataset_name="u2_posts",
    )


def main() -> None:
    """Ejecuta la extracción y la carga, e imprime el resumen de dlt."""
    pipeline = construir_pipeline()
    info = pipeline.run(posts())
    print(info)


if __name__ == "__main__":
    main()
