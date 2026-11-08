"""Corre el pipeline de ingesta de ciudades de Paraguay desde la API hacia DuckDB."""

from __future__ import annotations

import logging

import dlt
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dlt.resource(name="ciudades_py", write_disposition="replace")
def paraguay_cities_resource():
    """Extrae la lista de ciudades de Paraguay desde la API pública de countries.dev."""
    url = "https://countries.dev/cities?country=PY"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    # La API retorna una lista de diccionarios con las ciudades
    if isinstance(data, list):
        yield data
    elif isinstance(data, dict) and "data" in data:
        yield data["data"]
    else:
        yield data


@dlt.source
def paraguay_cities_source():
    """Fuente de datos de ciudades de Paraguay."""
    return paraguay_cities_resource()


def construir_pipeline() -> dlt.Pipeline:
    """Configura y retorna el pipeline de dlt para DuckDB."""
    return dlt.pipeline(
        pipeline_name="paraguay_cities_pipeline",
        destination=dlt.destinations.duckdb("data.duckdb"),
        dataset_name="raw_paraguay",
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(paraguay_cities_source())
    print(info)


if __name__ == "__main__":
    main()
