"""Consulta data.duckdb y muestra resultados por consola."""

from __future__ import annotations

from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).parent / "data.duckdb"


def main() -> None:
    con = duckdb.connect(str(RUTA_DB), read_only=True)
    try:
        total = con.execute("SELECT COUNT(*) FROM jsonplaceholder.posts").fetchone()[0]
        print(f"Total de posts cargados: {total}")

        filas = con.execute(
            "SELECT id, title FROM jsonplaceholder.posts WHERE user_id = 1 ORDER BY id LIMIT 5"
        ).fetchall()
        print("Primeros 5 posts del usuario 1:")
        for id_post, titulo in filas:
            print(f"  {id_post}: {titulo}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
