"""Script de verificación para consultar los datos cargados en DuckDB."""

from __future__ import annotations

from pathlib import Path

import duckdb

DB_PATH = Path("data.duckdb")


def verificar_datos(db_path: Path = DB_PATH) -> None:
    """Conecta a DuckDB y ejecuta consultas SQL de validación sobre la tabla cargada."""
    if not db_path.exists():
        raise FileNotFoundError(
            f"No se encontró la base de datos en '{db_path}'. Ejecuta primero pipeline.py."
        )

    with duckdb.connect(str(db_path), read_only=True) as conn:
        # 1. Conteo total de registros cargados
        total_ciudades = conn.execute("SELECT COUNT(*) FROM raw_paraguay.ciudades_py").fetchone()[0]
        print(f"Total de ciudades registradas: {total_ciudades}\n")

        # 2. Consulta filtrada y ordenada: Top 5 ciudades más pobladas
        print("Top 5 ciudades con mayor población en Paraguay:")
        top_ciudades = conn.execute(
            """
            SELECT geoname_id, name, population, latitude, longitude
            FROM raw_paraguay.ciudades_py
            WHERE population > 0
            ORDER BY population DESC
            LIMIT 5
            """
        ).fetchall()

        for geoname_id, nombre, poblacion, lat, lon in top_ciudades:
            print(f"  - {nombre} (ID: {geoname_id}): {poblacion:,} hab. [Lat: {lat}, Lon: {lon}]")

        # 3. Verificación del esquema generado automáticamente por dlt
        print("\nColumnas detectadas en la tabla (esquema de dlt):")
        columnas = conn.execute("DESCRIBE raw_paraguay.ciudades_py").fetchall()
        for col in columnas:
            print(f"  - {col[0]} ({col[1]})")


def main() -> None:
    verificar_datos()


if __name__ == "__main__":
    main()
