"""Ingesta idempotente: CSV de data/ -> data.duckdb con dlt.

Se puede ejecutar todas las veces que se quiera: las filas no se duplican.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

import dlt

DIR_DATA = Path(__file__).parent / "data"
RUTA_DB = Path(__file__).parent / "data.duckdb"
DATASET = "raw_minimercado"
TABLAS = ["productos", "vendedores", "compras", "ventas", "movimientos_stock"]


def convertir(valor: str) -> int | float | str:
    """Los CSV guardan todo como texto: devuelve el número si lo es, y si no, el texto."""
    for tipo in (int, float):
        try:
            return tipo(valor)
        except ValueError:
            pass
    return valor


def leer_csv(ruta: Path) -> Iterator[dict]:
    with open(ruta, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            yield {columna: convertir(valor) for columna, valor in fila.items()}


@dlt.source(name="minimercado")
def minimercado(directorio: Path = DIR_DATA):
    """Un recurso por CSV. Con 'merge' y clave primaria, una fila que ya existe se actualiza."""
    for nombre in TABLAS:
        yield dlt.resource(
            leer_csv(directorio / f"{nombre}.csv"),
            name=nombre,
            write_disposition="merge",
            primary_key="id",
        )


def construir_pipeline(ruta_db: Path = RUTA_DB) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="minimercado",
        destination=dlt.destinations.duckdb(str(ruta_db)),
        dataset_name=DATASET,
    )


def main() -> None:
    pipeline = construir_pipeline()
    info = pipeline.run(minimercado())
    print(info)


if __name__ == "__main__":
    main()
