"""Consulta con SQL los datos persistidos por el pipeline de la tarea U2."""

from pathlib import Path

import duckdb
from pipeline import BASE_DATOS


def verificar_datos(ruta_db=BASE_DATOS):
    """Consulta una base existente en modo de solo lectura."""
    ruta_db = Path(ruta_db)
    if not ruta_db.is_file():
        raise FileNotFoundError("No existe la base. Ejecutá primero pipeline.py.")

    with duckdb.connect(str(ruta_db), read_only=True) as conexion:
        total = conexion.execute("SELECT COUNT(*) FROM jsonplaceholder.posts").fetchone()[0]
        columnas = conexion.execute("DESCRIBE jsonplaceholder.posts").fetchall()
        por_usuario = conexion.execute(
            "SELECT user_id, COUNT(*) AS publicaciones "
            "FROM jsonplaceholder.posts GROUP BY user_id ORDER BY user_id"
        ).fetchall()
        muestra = conexion.execute(
            "SELECT id, user_id, title FROM jsonplaceholder.posts ORDER BY id LIMIT 5"
        ).fetchall()

    return {
        "total": total,
        "columnas": columnas,
        "por_usuario": por_usuario,
        "muestra": muestra,
    }


def main():
    resultados = verificar_datos()
    print(f"Base: {BASE_DATOS}")
    print(f"Total de publicaciones: {resultados['total']}")
    print("Columnas:", ", ".join(f"{c[0]} ({c[1]})" for c in resultados["columnas"]))
    print("Publicaciones por usuario:", resultados["por_usuario"])
    print("Primeras cinco publicaciones:")
    for fila in resultados["muestra"]:
        print(fila)


if __name__ == "__main__":
    main()
