"""Abre data.duckdb, ejecuta consultas SQL basicas y muestra los resultados."""

import sys
from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).resolve().parent / "data.duckdb"

CONSULTA_RESUMEN = """
    SELECT COUNT(*), MIN(date), MAX(date)
    FROM tipo_cambio.cotizaciones
"""

CONSULTA_POR_MONEDA = """
    SELECT quote, COUNT(*) AS dias, MIN(rate), MAX(rate), ROUND(AVG(rate), 2)
    FROM tipo_cambio.cotizaciones
    GROUP BY quote
    ORDER BY quote
"""

CONSULTA_ULTIMOS_DIAS_PYG = """
    SELECT date, rate
    FROM tipo_cambio.cotizaciones
    WHERE quote = 'PYG'
    ORDER BY date DESC
    LIMIT 5
"""


def main() -> None:
    if not RUTA_DB.exists():
        print(f"No se encontro {RUTA_DB}. Primero ejecuta pipeline.py.")
        sys.exit(1)

    with duckdb.connect(str(RUTA_DB), read_only=True) as con:
        total, desde, hasta = con.execute(CONSULTA_RESUMEN).fetchone()
        print(f"Registros cargados: {total} (desde {desde} hasta {hasta})\n")

        print("Cotizacion de 1 USD por moneda en el periodo:")
        print(f"  {'moneda':<7} {'dias':>5} {'minimo':>12} {'maximo':>12} {'promedio':>12}")
        for moneda, dias, minimo, maximo, promedio in con.execute(CONSULTA_POR_MONEDA).fetchall():
            print(f"  {moneda:<7} {dias:>5} {minimo:>12,.2f} {maximo:>12,.2f} {promedio:>12,.2f}")

        print("\nDolar en guaranies, ultimos 5 dias habiles (BCP):")
        for fecha, tasa in con.execute(CONSULTA_ULTIMOS_DIAS_PYG).fetchall():
            print(f"  {fecha}  {tasa:,.2f} PYG")


if __name__ == "__main__":
    main()
