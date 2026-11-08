"""Script de verificación de datos enriquecidos de PokeAPI en DuckDB."""

from __future__ import annotations

import duckdb


def verificar_base_datos(db_path: str = "data.duckdb") -> None:
    """Abre DuckDB y ejecuta consultas analíticas sobre los Pokémon cargados."""
    conexion = duckdb.connect(db_path)

    # 1. Conteo total de registros
    total = conexion.execute("SELECT COUNT(*) FROM raw_pokeapi.pokemon").fetchone()[0]
    print(f"Total de Pokémon registrados en DuckDB: {total}\n")

    # 2. Muestra de Pokémon con metadatos
    print("Muestra de Pokémon con metadatos enriquecidos:")
    registros = conexion.execute(
        "SELECT name, tipos, habilidades, movimientos FROM raw_pokeapi.pokemon LIMIT 5"
    ).fetchall()

    for nombre, tipos, habilidades, movimientos in registros:
        print(f"📌 {nombre.capitalize()}")
        print(f"   - Tipos: {tipos}")
        print(f"   - Habilidades: {habilidades}")
        print(f"   - Movimientos principales: {movimientos}\n")

    conexion.close()


def main() -> None:
    """Punto de entrada para la verificación."""
    verificar_base_datos()


if __name__ == "__main__":
    main()
