"""Pipeline: API JSONPlaceholder -> DuckDB (data.duckdb)."""

from __future__ import annotations

from pathlib import Path

import dlt
import requests

URL_POSTS = "https://jsonplaceholder.typicode.com/posts"
RUTA_DB = Path(__file__).parent / "data.duckdb"


def obtener_posts(url: str = URL_POSTS) -> list[dict]:
    respuesta = requests.get(url, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


@dlt.resource(name="posts", write_disposition="replace")
def posts():
    yield from obtener_posts()


def construir_pipeline() -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="jsonplaceholder",
        destination=dlt.destinations.duckdb(str(RUTA_DB)),
        dataset_name="jsonplaceholder",
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(posts())
    print(info)


if __name__ == "__main__":
    main()
