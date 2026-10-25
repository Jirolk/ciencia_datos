from __future__ import annotations

from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"


def consultar_resumen(ruta_db: Path = RUTA_DB) -> tuple[int, list[tuple[int, str]]]:
    if not ruta_db.exists():
        raise FileNotFoundError(f"No existe la base de datos: {ruta_db}")

    with duckdb.connect(str(ruta_db), read_only=True) as conexion:
        total = conexion.execute("SELECT COUNT(*) FROM u2_posts.posts").fetchone()[0]
        autores = conexion.execute(
            "SELECT user_id, COUNT(*) AS publicaciones "
            "FROM u2_posts.posts GROUP BY user_id ORDER BY publicaciones DESC, user_id LIMIT 5"
        ).fetchall()
    return total, autores


def main() -> None:
    total, autores = consultar_resumen()
    print(f"Registros totales: {total}")
    print("Autores con más publicaciones:")
    for user_id, publicaciones in autores:
        print(f"  usuario {user_id}: {publicaciones}")


if __name__ == "__main__":
    main()
