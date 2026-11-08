"""Análisis final y reporte de calidad sobre los marts de DuckDB.

* `python analisis.py`            -> imprime el resultado de consultas_analisis.sql
* `python analisis.py --calidad`  -> además valida la salida y escribe
                                      reportes/reporte_calidad.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

import duckdb
from pipeline import DB_PATH, RAIZ

SQL_PATH = RAIZ / "consultas_analisis.sql"


def cargar_consultas(ruta: Path = SQL_PATH) -> dict[str, str]:
    """Separa el archivo .sql en {nombre: consulta} usando los marcadores `-- name:`."""
    texto = ruta.read_text(encoding="utf-8")
    partes = re.split(r"^-- name:\s*(\S+)\s*$", texto, flags=re.MULTILINE)
    return {
        nombre: sql.strip().rstrip(";")
        for nombre, sql in zip(partes[1::2], partes[2::2], strict=False)
    }


def ejecutar_consultas(db_path: Path = DB_PATH) -> dict[str, tuple[list[str], list[tuple]]]:
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        resultados = {}
        for nombre, sql in cargar_consultas().items():
            cur = con.execute(sql)
            resultados[nombre] = ([d[0] for d in cur.description], cur.fetchall())
        return resultados
    finally:
        con.close()


def _imprimir(nombre: str, columnas: list[str], filas: list[tuple]) -> None:
    print(f"\n=== {nombre} ===")
    celdas = [columnas] + [[str(v) for v in f] for f in filas]
    anchos = [max(len(r[i]) for r in celdas) for i in range(len(columnas))]
    for n, fila in enumerate(celdas):
        print("  ".join(c.ljust(w) for c, w in zip(fila, anchos, strict=False)))
        if n == 0:
            print("  ".join("-" * w for w in anchos))


def generar_reporte_calidad(db_path: Path = DB_PATH) -> dict:
    """Valida la salida final del pipeline. Devuelve {'ok': bool, 'checks': [...]}."""
    con = duckdb.connect(str(db_path), read_only=True)

    def q(sql: str):
        valor = con.execute(sql).fetchone()[0]
        return float(valor) if isinstance(valor, Decimal) else valor

    checks: list[dict] = []

    def check(nombre: str, ok: bool, detalle: str) -> None:
        checks.append({"check": nombre, "ok": bool(ok), "detalle": detalle})

    try:
        # Volúmenes mínimos del enunciado
        minimos = {
            "productos": 20,
            "vendedores": 5,
            "compras": 100,
            "ventas": 500,
            "movimientos_stock": 1,
        }
        for tabla, minimo in minimos.items():
            n = q(f"select count(*) from raw.{tabla}")
            check(f"raw.{tabla} >= {minimo} filas", n >= minimo, f"{n} filas")

        # Sin duplicados (idempotencia de la ingesta)
        for tabla in minimos:
            dup = q(f"select count(*) - count(distinct id) from raw.{tabla}")
            check(f"raw.{tabla} sin ids duplicados", dup == 0, f"{dup} duplicados")

        # Cobertura temporal
        dias = q("select count(*) from marts.mart_ventas_diarias")
        check("cobertura >= 90 días", dias >= 90, f"{dias} días")

        # Conciliación entre capas
        neto_raw = q(
            "select round(sum(cantidad * precio_unitario * (1 - descuento)), 0) from raw.ventas"
        )
        neto_mart = q("select round(sum(ingreso_neto), 0) from marts.mart_ventas_diarias")
        check(
            "ingreso neto raw ≈ mart_ventas_diarias",
            abs(neto_raw - neto_mart) <= 5,
            f"raw={neto_raw} mart={neto_mart}",
        )

        gan_d = q("select sum(ganancia_bruta) from marts.mart_ventas_diarias")
        gan_p = q("select sum(ganancia_bruta) from marts.mart_rentabilidad_productos")
        check(
            "ganancia diaria = ganancia por producto",
            abs(gan_d - gan_p) < 0.01,
            f"{gan_d} vs {gan_p}",
        )

        # Inventario
        neg = q("select count(*) from intermediate.int_movimientos_stock where stock_acumulado < 0")
        check("stock nunca negativo", neg == 0, f"{neg} movimientos con stock negativo")

        # ABC
        part = q("select round(sum(participacion_pct), 1) from marts.mart_clasificacion_abc")
        check("ABC suma 100 %", abs(part - 100) <= 0.1, f"{part} %")
        clases = {
            r[0]
            for r in con.execute(
                "select distinct clasificacion_abc from marts.mart_clasificacion_abc"
            ).fetchall()
        }
        check(
            "ABC solo A/B/C",
            clases <= {"A", "B", "C"} and "A" in clases,
            f"clases={sorted(clases)}",
        )

        # Integridad referencial en raw
        huerf = q(
            "select count(*) from raw.ventas v "
            "left join raw.productos p on p.id = v.producto_id where p.id is null"
        )
        check("ventas sin producto huérfano", huerf == 0, f"{huerf} huérfanas")
    finally:
        con.close()

    return {"ok": all(c["ok"] for c in checks), "checks": checks}


def escribir_reporte(reporte: dict, destino: Path | None = None) -> Path:
    destino = destino or RAIZ / "reportes" / "reporte_calidad.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--db", type=Path, default=DB_PATH)
    ap.add_argument("--calidad", action="store_true", help="validar salida y escribir reporte JSON")
    args = ap.parse_args(argv)

    # La consola de Windows puede usar cp1252 y no todos los caracteres (≈, ≥)
    # son imprimibles: forzamos UTF-8 para que la impresión no truene.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    for nombre, (cols, filas) in ejecutar_consultas(args.db).items():
        _imprimir(nombre, cols, filas)

    if args.calidad:
        reporte = generar_reporte_calidad(args.db)
        ruta = escribir_reporte(reporte)
        print(f"\n=== reporte de calidad ({'OK' if reporte['ok'] else 'FALLÓ'}) -> {ruta} ===")
        for c in reporte["checks"]:
            print(f"[{'OK' if c['ok'] else 'FALLA'}] {c['check']}: {c['detalle']}")


if __name__ == "__main__":
    main()
