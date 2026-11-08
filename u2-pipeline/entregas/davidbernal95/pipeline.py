"""Extrae publicaciones de una API y las carga de forma persistente en DuckDB."""

from pathlib import Path

import dlt
from dlt.sources.helpers import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"
CARPETA = Path(__file__).resolve().parent
BASE_DATOS = CARPETA / "data.duckdb"


def obtener_posts():
    """Descarga y valida la respuesta antes de permitir una carga."""
    respuesta = requests.get(API_URL, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if not isinstance(datos, list):
        raise ValueError("La API debe devolver una lista.")
    if not datos:
        raise ValueError("La API devolvió una lista vacía; se cancela la carga.")

    campos = {"id", "userId", "title", "body"}
    for post in datos:
        if not isinstance(post, dict) or not campos.issubset(post):
            raise ValueError("Una publicación no tiene los campos obligatorios.")
        for campo in ("id", "userId"):
            valor = post[campo]
            if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
                raise ValueError(f"El campo {campo} debe ser un entero positivo.")
        if not isinstance(post["title"], str) or not isinstance(post["body"], str):
            raise ValueError("El título y el cuerpo deben ser texto.")
    return datos


@dlt.resource(name="posts", write_disposition="replace", primary_key="id")
def extraer_posts():
    """Expone las publicaciones validadas como un recurso de dlt."""
    yield from obtener_posts()


def ejecutar_pipeline(ruta_db=BASE_DATOS, directorio_estado=None):
    """Carga los datos; permite usar rutas temporales en las pruebas."""
    ruta_db = Path(ruta_db).resolve()
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    if directorio_estado is None:
        directorio_estado = ruta_db.parent / ".dlt_pipelines"

    flujo = dlt.pipeline(
        pipeline_name="u2_posts_davidbernal95",
        destination=dlt.destinations.duckdb(str(ruta_db)),
        dataset_name="jsonplaceholder",
        pipelines_dir=str(directorio_estado),
    )
    return flujo.run(extraer_posts())


if __name__ == "__main__":
    print(ejecutar_pipeline())
