"""Extrae publicaciones de una API pública y las carga en DuckDB con dlt."""

from pathlib import Path

import dlt
from dlt.sources.helpers import requests

URL_API = "https://jsonplaceholder.typicode.com/posts"
RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"
CAMPOS_REQUERIDOS = {"id", "userId", "title", "body"}


@dlt.resource(name="publicaciones", write_disposition="replace")
def publicaciones(url: str = URL_API):
    """Obtiene y valida una respuesta completa antes de entregar sus registros."""
    respuesta = requests.get(url, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if not isinstance(datos, list):
        raise ValueError("La API debe devolver una lista de publicaciones.")
    if not datos:
        raise ValueError("La API devolvió una lista vacía; se cancela la carga.")
    for registro in datos:
        if not isinstance(registro, dict) or not CAMPOS_REQUERIDOS.issubset(registro):
            raise ValueError("Una publicación no contiene los campos esperados.")

    yield from datos


def construir_pipeline(ruta_db: Path = RUTA_DB) -> dlt.Pipeline:
    """Configura una base persistente y guarda el estado junto a esa base."""
    ruta_db = Path(ruta_db).resolve()
    return dlt.pipeline(
        pipeline_name="publicaciones_api",
        destination=dlt.destinations.duckdb(str(ruta_db)),
        dataset_name="api_publica",
        pipelines_dir=str(ruta_db.parent / ".dlt" / "pipelines"),
    )


def main() -> None:
    pipeline = construir_pipeline()
    resultado = pipeline.run(publicaciones())
    print(resultado)
    print(f"Base de datos guardada en: {RUTA_DB}")


if __name__ == "__main__":
    main()
