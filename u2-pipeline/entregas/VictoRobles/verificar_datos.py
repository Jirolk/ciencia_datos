"""Consulta data.duckdb y muestra un resumen del pronóstico."""

from __future__ import annotations

from pathlib import Path

import duckdb

RUTA_DB = Path(__file__).parent / "data.duckdb"


def main() -> None:
    con = duckdb.connect(str(RUTA_DB), read_only=True)
    try:
        total = con.execute("SELECT COUNT(*) FROM clima.pronostico_horario").fetchone()[0]
        print(f"Horas cargadas: {total}")

        maxima = con.execute(
            "SELECT time, temperature_2m FROM clima.pronostico_horario "
            "ORDER BY temperature_2m DESC LIMIT 1"
        ).fetchone()
        print(f"Hora más calurosa: {maxima[0]} con {maxima[1]} °C")

        con_lluvia = con.execute(
            "SELECT COUNT(*) FROM clima.pronostico_horario WHERE precipitation > 0"
        ).fetchone()[0]
        print(f"Horas con lluvia: {con_lluvia}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
