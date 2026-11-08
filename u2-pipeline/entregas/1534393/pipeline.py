"""Pipeline de datos con dlt para cargar usuarios desde la API JSONPlaceholder a DuckDB."""

from pathlib import Path

import dlt
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


@dlt.resource(name="usuarios", write_disposition="replace")
def obtener_usuarios(url: str = API_URL):
    """Extrae la lista de usuarios desde la API pública de JSONPlaceholder."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        yield from data
    elif isinstance(data, dict):
        yield data


def ejecutar_pipeline():
    """Ejecuta el pipeline de dlt hacia la base DuckDB local."""
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "data.duckdb"

    pipeline = dlt.pipeline(
        pipeline_name="usuarios_pipeline",
        destination=dlt.destinations.duckdb(str(db_path)),
        dataset_name="datos_publicos",
    )

    info_carga = pipeline.run(obtener_usuarios())
    print("Carga finalizada con éxito:")
    print(info_carga)
    return info_carga


if __name__ == "__main__":
    ejecutar_pipeline()
