"""Pipeline: pronóstico por hora de Open-Meteo (Asunción) -> DuckDB (data.duckdb)."""

from __future__ import annotations

from pathlib import Path

import dlt
import requests

URL_API = "https://api.open-meteo.com/v1/forecast"
PARAMETROS = {
    "latitude": -25.26,
    "longitude": -57.58,
    "hourly": "temperature_2m,precipitation",
    "forecast_days": 3,
    "timezone": "auto",
}
RUTA_DB = Path(__file__).parent / "data.duckdb"


def pedir_pronostico(url: str = URL_API, parametros: dict | None = None) -> dict:
    respuesta = requests.get(url, params=parametros or PARAMETROS, timeout=15)
    respuesta.raise_for_status()
    return respuesta.json()


def filas_por_hora(datos: dict) -> list[dict]:
    horario = datos.get("hourly", {})
    filas = []
    for hora, temp, lluvia in zip(
        horario.get("time", []),
        horario.get("temperature_2m", []),
        horario.get("precipitation", []),
        strict=True,
    ):
        filas.append(
            {
                "time": hora,
                "temperature_2m": temp,
                "precipitation": lluvia,
                "latitude": datos.get("latitude"),
                "longitude": datos.get("longitude"),
            }
        )
    return filas


@dlt.resource(name="pronostico_horario", write_disposition="replace")
def pronostico_horario():
    yield from filas_por_hora(pedir_pronostico())


def construir_pipeline() -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="pronostico_asuncion",
        destination=dlt.destinations.duckdb(str(RUTA_DB)),
        dataset_name="clima",
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(pronostico_horario())
    print(info)


if __name__ == "__main__":
    main()
