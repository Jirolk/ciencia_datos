"""Pipeline de ingesta: cotizaciones oficiales del Banco Central del Paraguay -> DuckDB.

Fuente: API publica Frankfurter (https://frankfurter.dev).
Destino: data.duckdb, esquema tipo_cambio, tabla cotizaciones.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import dlt
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

URL_COTIZACIONES = "https://api.frankfurter.dev/v2/rates"
PROVEEDOR = "BCP"
MONEDA_BASE = "USD"
MONEDAS = "PYG,BRL,ARS,EUR"
FECHA_INICIAL = "2026-01-01"

CARPETA = Path(__file__).resolve().parent
RUTA_DB = CARPETA / "data.duckdb"


def pedir_cotizaciones(desde: str) -> list[dict]:
    """Pide a la API las cotizaciones desde una fecha (YYYY-MM-DD) hasta hoy.
    Si la API responde con error (404, 422, 500...) o no hay conexion, lanza una excepcion."""
    parametros = {
        "from": desde,
        "base": MONEDA_BASE,
        "quotes": MONEDAS,
        "providers": PROVEEDOR,
    }
    respuesta = requests.get(URL_COTIZACIONES, params=parametros, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


@dlt.resource(
    name="cotizaciones",
    primary_key=("date", "quote"),
    write_disposition="merge",
    # La API manda la fecha como texto ("2026-10-01"); sin esta pista dlt la guarda como VARCHAR.
    columns={"date": {"data_type": "date"}},
)
def cotizaciones(
    # dlt pide declarar el cursor incremental como valor por defecto del argumento.
    fecha=dlt.sources.incremental("date", initial_value=FECHA_INICIAL),  # noqa: B008
) -> Iterator[list[dict]]:
    """Trae solo las fechas nuevas: fecha.last_value es la ultima fecha cargada en la
    corrida anterior (dlt la guarda en su estado). La primera vez usa FECHA_INICIAL."""
    logger.info("Pidiendo cotizaciones desde %s", fecha.last_value)
    registros = pedir_cotizaciones(desde=str(fecha.last_value))
    logger.info("La API devolvio %d registros", len(registros))
    if registros:
        yield registros


@dlt.source(name="tipo_cambio")
def tipo_cambio_source():
    return cotizaciones()


def construir_pipeline(ruta_db: Path = RUTA_DB, pipelines_dir: str | None = None) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="tipo_cambio_bcp",
        destination=dlt.destinations.duckdb(str(ruta_db)),
        dataset_name="tipo_cambio",
        pipelines_dir=pipelines_dir,
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(tipo_cambio_source())
    print(info)
    print(f"Base de datos generada en: {RUTA_DB}")


if __name__ == "__main__":
    main()
