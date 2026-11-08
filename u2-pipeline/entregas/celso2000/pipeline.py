"""Pipeline dlt: extrae usuarios de JSONPlaceholder y los carga en DuckDB."""

import dlt
from dlt.sources.helpers import requests

URL = "https://jsonplaceholder.typicode.com/users"
DB = "data.duckdb"
DATASET = "jsonplaceholder"


@dlt.resource(name="users", write_disposition="replace")
def users():
    """Entrega la lista de usuarios que devuelve la API."""
    respuesta = requests.get(URL, timeout=30)
    respuesta.raise_for_status()
    yield respuesta.json()


def run_pipeline():
    """Extrae, normaliza y carga los usuarios en DuckDB."""
    pipeline = dlt.pipeline(
        pipeline_name="mi_pipeline",
        destination=dlt.destinations.duckdb(DB),
        dataset_name=DATASET,
    )
    info = pipeline.run(users())
    print(info)
    return info


if __name__ == "__main__":
    run_pipeline()
