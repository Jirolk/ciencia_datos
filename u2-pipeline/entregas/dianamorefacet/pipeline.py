"""Pipeline de ingesta utilizando dlt y DuckDB desde Rick and Morty API."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator

import dlt
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

API_URL = "https://rickandmortyapi.com/api/character"
DB_PATH = "data.duckdb"
COOLDOWN = 0.5


@dlt.resource(name="personajes", write_disposition="replace")
def obtener_personajes() -> Iterator[dict]:
    """Extrae personajes desde Rick and Morty API."""

    url = API_URL

    while url:
        logging.info("Consultando %s", url)

        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()

        contenido = respuesta.json()

        for personaje in contenido["results"]:
            yield {
                "id": personaje["id"],
                "name": personaje["name"],
                "status": personaje["status"],
                "species": personaje["species"],
                "gender": personaje["gender"],
                "origin": personaje["origin"]["name"],
                "location": personaje["location"]["name"],
            }

        url = contenido["info"]["next"]

        if url:
            logging.info(
                "Esperando %.1f segundos antes de la siguiente página...",
                COOLDOWN,
            )
            time.sleep(COOLDOWN)


def construir_pipeline() -> dlt.Pipeline:
    """Configura el pipeline apuntando a DuckDB."""

    return dlt.pipeline(
        pipeline_name="rick_morty_pipeline",
        destination=dlt.destinations.duckdb(DB_PATH),
        dataset_name="raw_rickmorty",
    )


def main() -> None:
    """Ejecuta la extracción y carga."""

    pipeline = construir_pipeline()

    info = pipeline.run(obtener_personajes())

    print(info)


if __name__ == "__main__":
    main()
