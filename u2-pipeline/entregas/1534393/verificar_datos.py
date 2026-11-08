"""Script para verificar y consultar los datos cargados en DuckDB."""

from pathlib import Path

import duckdb


def consultar_base():
    """Conecta a data.duckdb y ejecuta consultas analíticas en SQL."""
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "data.duckdb"

    if not db_path.exists():
        raise FileNotFoundError(f"No se encontró la base de datos en {db_path}")

    # Conexión en modo solo lectura a DuckDB
    con = duckdb.connect(database=str(db_path), read_only=True)

    print("--- 1. Conteo total de usuarios cargados ---")
    total = con.execute("SELECT COUNT(*) FROM datos_publicos.usuarios").fetchone()[0]
    print(f"Total de registros: {total}\n")

    print("--- 2. Primeros 3 usuarios (ID, Nombre, Email, Ciudad) ---")
    filas = con.execute(
        """
        SELECT id, name, email, address__city 
        FROM datos_publicos.usuarios 
        ORDER BY id 
        LIMIT 3
        """
    ).fetchall()

    for fila in filas:
        print(f"ID: {fila[0]} | Nombre: {fila[1]} | Email: {fila[2]} | Ciudad: {fila[3]}")

    con.close()
    return total


if __name__ == "__main__":
    consultar_base()
