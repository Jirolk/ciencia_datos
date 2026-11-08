"""Pipeline de ingesta utilizando dlt y DuckDB desde PokeAPI con metadatos detallados."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from pathlib import Path

import dlt
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
DB_PATH = Path("data.duckdb")


@dlt.resource(name="pokemon", write_disposition="replace")
def obtener_pokemon_api() -> Iterator[list[dict]]:
    """Extrae Pokémon con tipos, habilidades y movimientos desde PokeAPI."""
    url = "https://pokeapi.co/api/v2/pokemon?limit=40&offset=0"

    max_paginas = 5
    paginas_procesadas = 0

    while url and paginas_procesadas < max_paginas:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        pokemon_lista = datos.get("results", [])
        detalles_pagina = []

        for item in pokemon_lista:
            res_detalle = requests.get(item["url"], timeout=10)
            if res_detalle.status_code == 200:
                detalle = res_detalle.json()

                tipos = [t["type"]["name"] for t in detalle.get("types", [])]
                habilidades = [h["ability"]["name"] for h in detalle.get("abilities", [])]
                movimientos = [m["move"]["name"] for m in detalle.get("moves", [])[:5]]

                detalles_pagina.append(
                    {
                        "id": detalle.get("id"),
                        "name": detalle.get("name"),
                        "height": detalle.get("height"),
                        "weight": detalle.get("weight"),
                        "tipos": json.dumps(tipos),
                        "habilidades": json.dumps(habilidades),
                        "movimientos": json.dumps(movimientos),
                        "url": item["url"],
                    }
                )
            time.sleep(0.1)

        yield detalles_pagina

        url = datos.get("next")
        paginas_procesadas += 1
        if url:
            time.sleep(0.5)


def construir_pipeline() -> dlt.Pipeline:
    """Configura el pipeline dlt apuntando al destino DuckDB."""
    return dlt.pipeline(
        pipeline_name="pokeapi_pipeline",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name="raw_pokeapi",
    )


def main() -> None:
    """Ejecuta la extracción y carga de datos desde cero."""
    if DB_PATH.exists():
        logging.info(
            "Se detectó una base de datos DuckDB existente en %s. Eliminando...",
            DB_PATH,
        )
        DB_PATH.unlink()

    pipeline = construir_pipeline()
    info = pipeline.run(obtener_pokemon_api())
    print(info)


if __name__ == "__main__":
    main()
