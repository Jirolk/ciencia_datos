"""Verifica la carga: abre data.duckdb y ejecuta consultas SQL básicas."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"
TABLA = "rick_and_morty.personajes"


def imprimir(titulo: str, columnas: list[str], filas: list[tuple]) -> None:
    print(f"\n== {titulo}")
    print(" | ".join(columnas))
    for fila in filas:
        print(" | ".join(str(v) for v in fila))


def consultar(con: duckdb.DuckDBPyConnection, sql: str) -> tuple[list[str], list]:
    cursor = con.execute(sql)
    columnas = [d[0] for d in cursor.description]
    return columnas, cursor.fetchall()


def main(ruta_db: Path = RUTA_DB) -> int:
    if not ruta_db.exists():
        print(f"No existe {ruta_db}. Ejecuta primero pipeline.py")
        return 1

    with duckdb.connect(str(ruta_db), read_only=True) as con:
        total = con.execute(f"SELECT COUNT(*) FROM {TABLA}").fetchone()[0]
        print(f"Registros en {TABLA}: {total}")

        imprimir(
            "Personajes por estado",
            *consultar(
                con,
                f"SELECT estado, COUNT(*) AS n FROM {TABLA} GROUP BY estado ORDER BY n DESC",
            ),
        )
        imprimir(
            "Top 5 especies",
            *consultar(
                con,
                f"SELECT especie, COUNT(*) AS n FROM {TABLA} "
                "GROUP BY especie ORDER BY n DESC LIMIT 5",
            ),
        )
        imprimir(
            "Humanos vivos con más episodios",
            *consultar(
                con,
                f"SELECT id, nombre, n_episodios FROM {TABLA} "
                "WHERE especie = 'Human' AND estado = 'Alive' "
                "ORDER BY n_episodios DESC, id LIMIT 5",
            ),
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
