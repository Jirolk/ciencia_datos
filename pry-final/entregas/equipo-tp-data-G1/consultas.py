"""Ejecuta las consultas finales de dbt_project/analyses/ sobre data.duckdb y las imprime."""

from __future__ import annotations

from pathlib import Path

import duckdb

DIR = Path(__file__).parent
RUTA_DB = DIR / "data.duckdb"
DIR_CONSULTAS = DIR / "dbt_project" / "analyses"


def separar_consultas(texto: str) -> list[str]:
    """Divide un archivo .sql en consultas individuales (separadas por ';')."""
    return [bloque.strip() for bloque in texto.split(";") if bloque.strip()]


def main() -> None:
    con = duckdb.connect(str(RUTA_DB), read_only=True)
    try:
        for archivo in sorted(DIR_CONSULTAS.glob("*.sql")):
            print(f"\n===== {archivo.name} =====")
            for consulta in separar_consultas(archivo.read_text(encoding="utf-8")):
                titulo = consulta.splitlines()[0]
                print(f"\n{titulo}")
                print(con.sql(consulta))
    finally:
        con.close()


if __name__ == "__main__":
    main()
