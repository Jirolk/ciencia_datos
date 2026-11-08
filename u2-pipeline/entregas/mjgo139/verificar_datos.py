"""Abre data.duckdb, ejecuta consultas SQL y muestra los resultados por consola."""

from pathlib import Path

import duckdb

RUTA_BD = Path(__file__).resolve().parent / "data.duckdb"
ESQUEMA = "jsonplaceholder"


def contar(conexion: duckdb.DuckDBPyConnection, tabla: str) -> int:
    """Cuenta las filas de una tabla del esquema."""
    return conexion.execute(f"SELECT COUNT(*) FROM {ESQUEMA}.{tabla}").fetchone()[0]


def avance_por_usuario(conexion: duckdb.DuckDBPyConnection) -> list[tuple]:
    """Une usuarios y tareas: cuántas tareas tiene cada uno y cuántas completó."""
    consulta = f"""
        SELECT u.name, u.address__city, COUNT(t.id) AS total, SUM(t.completed::INT) AS hechas
        FROM {ESQUEMA}.usuarios AS u
        JOIN {ESQUEMA}.tareas AS t ON t.user_id = u.id
        GROUP BY u.name, u.address__city
        ORDER BY hechas DESC, u.name
    """
    return conexion.execute(consulta).fetchall()


def tareas_pendientes(conexion: duckdb.DuckDBPyConnection) -> int:
    """Filtra las tareas que todavía no están completadas."""
    consulta = f"SELECT COUNT(*) FROM {ESQUEMA}.tareas WHERE NOT completed"
    return conexion.execute(consulta).fetchone()[0]


def main() -> None:
    if not RUTA_BD.exists():
        print(f"No existe {RUTA_BD.name}. Ejecuta primero pipeline.py")
        return
    with duckdb.connect(str(RUTA_BD), read_only=True) as conexion:
        print(f"Usuarios: {contar(conexion, 'usuarios')}")
        print(f"Tareas: {contar(conexion, 'tareas')}")
        print(f"Tareas pendientes: {tareas_pendientes(conexion)}")
        print("\nAvance por usuario (completadas / total):")
        for nombre, ciudad, total, hechas in avance_por_usuario(conexion):
            print(f"  {nombre} ({ciudad}): {hechas}/{total}")


if __name__ == "__main__":
    main()
