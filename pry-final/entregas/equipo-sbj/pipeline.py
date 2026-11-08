"""Ingesta de los CSV sintéticos hacia DuckDB usando `dlt`.

* Origen : archivos CSV de ./data (generados por generar_datos.py)
* Destino: base DuckDB local `data.duckdb`, esquema `raw`
* Idempotencia: cada recurso usa `write_disposition="merge"` con
  `primary_key="id"`, por lo que reejecutar el script actualiza las filas
  existentes en lugar de duplicarlas.

Uso:
    python pipeline.py
    python pipeline.py --data-dir data --db data.duckdb

La ruta de la base también puede fijarse con la variable de entorno
DUCKDB_PATH (la usan dbt, Dagster y los tests).
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from datetime import date
from pathlib import Path

import dlt
import duckdb

RAIZ = Path(__file__).resolve().parent
DATA_DIR = RAIZ / "data"
DBT_DIR = RAIZ / "dbt_project"
DB_PATH = Path(os.environ.get("DUCKDB_PATH", RAIZ / "data.duckdb"))
DATASET = "raw"

# Conversores de tipo por columna, para que dlt cree columnas tipadas
# (INTEGER / DOUBLE / DATE / VARCHAR) y no todo como texto.
_int = int
_float = float
_fecha = date.fromisoformat
_texto = str


def _int_nulo(s: str) -> int | None:
    return int(s) if s != "" else None


TABLAS: dict[str, dict[str, Callable]] = {
    "productos": {
        "id": _int,
        "nombre": _texto,
        "categoria": _texto,
        "costo_unitario": _float,
        "precio_venta": _float,
        "stock_inicial": _int,
    },
    "vendedores": {"id": _int, "nombre": _texto, "sucursal": _texto, "fecha_alta": _fecha},
    "compras": {
        "id": _int,
        "fecha": _fecha,
        "producto_id": _int,
        "cantidad": _int,
        "costo_unitario": _float,
        "proveedor": _texto,
    },
    "ventas": {
        "id": _int,
        "fecha": _fecha,
        "producto_id": _int,
        "cantidad": _int,
        "precio_unitario": _float,
        "descuento": _float,
        "vendedor_id": _int,
    },
    "movimientos_stock": {
        "id": _int,
        "fecha": _fecha,
        "producto_id": _int,
        "tipo": _texto,
        "cantidad": _int,
        "motivo": _texto,
        "referencia_id": _int_nulo,
    },
}

_TIPOS_DLT = {_int: "bigint", _int_nulo: "bigint", _float: "double", _fecha: "date", _texto: "text"}


def _leer_csv(ruta: Path, conversores: dict[str, Callable]) -> Iterator[dict]:
    with ruta.open(newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            yield {col: conv(fila[col]) for col, conv in conversores.items()}


def _crear_recurso(nombre: str, conversores: dict[str, Callable], data_dir: Path):
    columnas = {c: {"data_type": _TIPOS_DLT[conv]} for c, conv in conversores.items()}

    @dlt.resource(name=nombre, primary_key="id", write_disposition="merge", columns=columnas)
    def recurso():
        yield from _leer_csv(data_dir / f"{nombre}.csv", conversores)

    return recurso


@dlt.source(name="minimercado")
def minimercado_source(data_dir: Path = DATA_DIR):
    """Fuente dlt: un recurso por cada CSV."""
    return [_crear_recurso(n, conv, Path(data_dir)) for n, conv in TABLAS.items()]


def ejecutar_ingesta(
    data_dir: Path = DATA_DIR, db_path: Path = DB_PATH, pipelines_dir: Path | None = None
):
    """Carga los CSV en DuckDB y devuelve la información de carga de dlt."""
    db_path = Path(db_path).resolve()
    pipeline = dlt.pipeline(
        pipeline_name="minimercado",
        destination=dlt.destinations.duckdb(str(db_path)),
        dataset_name=DATASET,
        pipelines_dir=str(pipelines_dir or RAIZ / ".dlt_pipelines"),
    )
    return pipeline.run(minimercado_source(Path(data_dir)))


def contar_filas(db_path: Path = DB_PATH) -> dict[str, int]:
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return {t: con.execute(f"select count(*) from {DATASET}.{t}").fetchone()[0] for t in TABLAS}
    finally:
        con.close()


def ejecutar_dbt(db_path: Path = DB_PATH, comando: str = "build") -> None:
    """Ejecuta `dbt <comando>` sobre dbt_project/ apuntando a `db_path`.

    Se lanza en un subproceso para que dbt libere el archivo DuckDB al terminar
    (DuckDB admite un solo proceso escritor). Es lo mismo que correr en la
    terminal `dbt build --project-dir dbt_project --profiles-dir dbt_project`.
    Lanza RuntimeError si algún modelo o prueba falla.
    """
    entorno = {**os.environ, "DUCKDB_PATH": str(Path(db_path).resolve())}
    cmd = [
        sys.executable,
        "-c",
        "import sys; from dbt.cli.main import cli; sys.exit(cli())",
        comando,
        "--project-dir",
        str(DBT_DIR),
        "--profiles-dir",
        str(DBT_DIR),
    ]
    resultado = subprocess.run(cmd, env=entorno, cwd=RAIZ, capture_output=True, text=True)
    print(resultado.stdout)
    if resultado.returncode != 0:
        raise RuntimeError(
            f"dbt {comando} falló (código {resultado.returncode}):\n"
            f"{resultado.stdout[-3000:]}\n{resultado.stderr[-1000:]}"
        )


def main(argv: list[str] | None = None) -> dict[str, int]:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--data-dir", type=Path, default=DATA_DIR)
    ap.add_argument("--db", type=Path, default=DB_PATH)
    args = ap.parse_args(argv)
    info = ejecutar_ingesta(args.data_dir, args.db)
    print(info)
    filas = contar_filas(args.db)
    print(f"Filas en {args.db.name} (esquema {DATASET}): {filas}")
    return filas


if __name__ == "__main__":
    main()
