"""Verificación de datos cargados en DuckDB."""

import duckdb

DB_PATH = "data.duckdb"


def main() -> None:
    """Ejecuta consultas de verificación."""

    conn = duckdb.connect(DB_PATH)

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM raw_rickmorty.personajes
        """
    ).fetchone()[0]

    print("=" * 50)
    print("VERIFICACIÓN DE DATOS")
    print("=" * 50)
    print(f"Total de personajes cargados: {total}")

    personajes_vivos = conn.execute(
        """
        SELECT name, species
        FROM raw_rickmorty.personajes
        WHERE status = 'Alive'
        LIMIT 10
        """
    ).fetchall()

    print("\nPrimeros personajes vivos:")

    for nombre, especie in personajes_vivos:
        print(f"- {nombre} ({especie})")

    conteo_estados = conn.execute(
        """
        SELECT
            status,
            COUNT(*) AS cantidad
        FROM raw_rickmorty.personajes
        GROUP BY status
        ORDER BY cantidad DESC
        """
    ).fetchall()

    print("\nCantidad de personajes por estado:")

    for estado, cantidad in conteo_estados:
        print(f"- {estado}: {cantidad}")

    conn.close()


if __name__ == "__main__":
    main()
