"""Consulta la base creada por pipeline.py sin modificarla."""

from pathlib import Path

import duckdb
from pipeline import RUTA_DB


def verificar_datos(ruta_db: Path = RUTA_DB) -> None:
    ruta_db = Path(ruta_db)
    if not ruta_db.is_file():
        raise FileNotFoundError("No existe data.duckdb. Ejecuta primero pipeline.py.")

    with duckdb.connect(str(ruta_db), read_only=True) as conexion:
        total = conexion.execute("SELECT COUNT(*) FROM api_publica.publicaciones").fetchone()[0]
        del_usuario_1 = conexion.execute(
            "SELECT COUNT(*) FROM api_publica.publicaciones WHERE user_id = 1"
        ).fetchone()[0]
        ejemplos = conexion.execute(
            "SELECT id, user_id, title FROM api_publica.publicaciones ORDER BY id LIMIT 5"
        ).fetchall()
        columnas = conexion.execute("DESCRIBE api_publica.publicaciones").fetchall()

    print(f"Total de publicaciones: {total}")
    print(f"Publicaciones del usuario 1: {del_usuario_1}")
    print("Primeras cinco publicaciones (id, user_id, title):")
    for fila in ejemplos:
        print(fila)
    print("Columnas y tipos detectados por dlt:")
    for columna in columnas:
        print(f"{columna[0]}: {columna[1]}")


if __name__ == "__main__":
    verificar_datos()
