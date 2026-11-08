"""Consulta data.duckdb con SQL y muestra los resultados por consola."""

from __future__ import annotations

from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"
ESQUEMA = "u2_posts"


def main() -> None:
    """Abre la base en modo lectura y ejecuta conteo y filtrado."""
    if not RUTA_DB.exists():
        raise SystemExit(f"No existe {RUTA_DB}. Ejecuta primero pipeline.py.")
    conexion = duckdb.connect(str(RUTA_DB), read_only=True)
    try:
        total = conexion.execute(f"SELECT COUNT(*) FROM {ESQUEMA}.posts").fetchone()[0]
        print(f"Total de posts cargados: {total}")

        filas = conexion.execute(
            f"SELECT id, title FROM {ESQUEMA}.posts WHERE user_id = 1 ORDER BY id LIMIT 5"
        ).fetchall()
        print("Primeros 5 posts del usuario 1:")
        for fila in filas:
            print("  ", fila)
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
