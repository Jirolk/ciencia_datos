from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import dlt

API_URL = "https://jsonplaceholder.typicode.com/posts"
CARPETA = Path(__file__).resolve().parent
RUTA_DB = CARPETA / "data.duckdb"


def obtener_publicaciones(url: str = API_URL, timeout: float = 15.0) -> list[dict[str, Any]]:
    try:
        with urlopen(url, timeout=timeout) as respuesta:
            contenido = respuesta.read().decode("utf-8")
    except HTTPError as error:
        raise RuntimeError(f"La API respondió con el estado HTTP {error.code}") from error
    except URLError as error:
        raise RuntimeError("No fue posible conectar con la API pública") from error

    datos = json.loads(contenido)
    if not isinstance(datos, list):
        raise RuntimeError("La API no devolvió una lista de publicaciones")
    return datos


@dlt.resource(name="posts", write_disposition="replace")
def recurso_publicaciones(
    publicaciones: Iterable[dict[str, Any]] | None = None,
) -> Iterable[dict[str, Any]]:
    if publicaciones is None:
        publicaciones = obtener_publicaciones()
    yield from publicaciones


def construir_pipeline() -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="jsonplaceholder_posts",
        destination=dlt.destinations.duckdb(credentials=str(RUTA_DB)),
        dataset_name="u2_posts",
    )


def main() -> None:
    publicaciones = obtener_publicaciones()
    pipeline = construir_pipeline()
    carga = pipeline.run(recurso_publicaciones(publicaciones))
    print(f"Pipeline completado: {len(publicaciones)} publicaciones cargadas en {RUTA_DB}")
    print(carga)


if __name__ == "__main__":
    main()
