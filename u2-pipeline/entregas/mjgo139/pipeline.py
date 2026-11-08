"""Pipeline de datos: usuarios y tareas de JSONPlaceholder -> DuckDB con dlt."""

from pathlib import Path

import dlt
import requests

URL_BASE = "https://jsonplaceholder.typicode.com"
RUTA_BD = Path(__file__).resolve().parent / "data.duckdb"


def obtener(endpoint: str) -> list[dict]:
    """Pide un endpoint de la API y devuelve la lista de registros en JSON."""
    respuesta = requests.get(f"{URL_BASE}/{endpoint}", timeout=30)
    respuesta.raise_for_status()
    return respuesta.json()


@dlt.resource(name="usuarios", primary_key="id", write_disposition="replace")
def usuarios():
    """Usuarios con su dirección y empresa; dlt aplana esos datos anidados."""
    yield obtener("users")


@dlt.resource(name="tareas", primary_key="id", write_disposition="replace")
def tareas():
    """Tareas de cada usuario, con su estado de completada."""
    yield obtener("todos")


@dlt.source(name="jsonplaceholder")
def jsonplaceholder():
    """Agrupa los dos recursos para cargarlos juntos."""
    return [usuarios(), tareas()]


def construir_pipeline(ruta_bd: Path = RUTA_BD) -> dlt.Pipeline:
    """Configura el pipeline para guardar en data.duckdb, esquema jsonplaceholder."""
    return dlt.pipeline(
        pipeline_name="jsonplaceholder",
        destination=dlt.destinations.duckdb(credentials=str(ruta_bd)),
        dataset_name="jsonplaceholder",
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(jsonplaceholder())
    print(info)


if __name__ == "__main__":
    main()
