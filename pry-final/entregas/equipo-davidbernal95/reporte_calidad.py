"""Concilia los resultados de los marts y ejecuta las consultas de negocio."""

import json
from pathlib import Path

import duckdb

from configuracion import PROYECTO, TABLAS, carpeta_trabajo


def consultar(conexion, consulta):
    cursor = conexion.execute(consulta)
    columnas = [col[0] for col in cursor.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]


def reporte_calidad(base=None):
    trabajo = carpeta_trabajo()
    base = Path(base).resolve() if base is not None else trabajo / "data.duckdb"
    if not base.is_file():
        raise FileNotFoundError(f"Falta la base de análisis: {base}")

    with duckdb.connect(str(base), read_only=True) as conexion:
        origen = {
            tabla: conexion.execute(f"select count(*) from raw_minimercado.{tabla}").fetchone()[0]
            for tabla in TABLAS
        }
        cifras = conexion.execute("""
            select
                (select coalesce(sum(importe_neto), 0) from analitica.stg_ventas),
                (select sum(facturacion_neta) from analitica.mart_ventas_diarias),
                (select sum(facturacion_neta) from analitica.mart_rentabilidad_productos),
                (select sum(facturacion_neta) from analitica.mart_desempeno_vendedores),
                (select sum(facturacion_neta) from analitica.mart_abc_productos)
        """).fetchone()
        detalle_ventas = conexion.execute("""
            select count(*), coalesce(sum(importe_neto), 0) from analitica.fct_ventas
        """).fetchone()
        detalle_compras = conexion.execute("select count(*) from analitica.fct_compras").fetchone()[
            0
        ]
        saldos_mal = conexion.execute("""
            with compras as (
                select producto_id, sum(cantidad) as unidades
                from analitica.stg_compras group by producto_id
            ),
            ventas as (
                select producto_id, sum(cantidad) as unidades
                from analitica.stg_ventas group by producto_id
            )
            select count(*)
            from analitica.stg_productos p
            left join compras c using (producto_id)
            left join ventas v using (producto_id)
            left join analitica.mart_rotacion_inventario i using (producto_id)
            where i.stock_actual is distinct from
                p.stock_inicial + coalesce(c.unidades, 0) - coalesce(v.unidades, 0)
        """).fetchone()[0]
        indicadores = {
            ruta.stem: consultar(conexion, ruta.read_text(encoding="utf-8"))
            for ruta in sorted((PROYECTO / "sql").glob("*.sql"))
        }

    estadistica = indicadores["01_estadistica"][0]
    if (
        origen["productos"] < 20
        or origen["vendedores"] < 5
        or origen["compras"] < 100
        or origen["ventas"] < 500
        or estadistica["dias"] < 90
        or origen["movimientos_stock"] != origen["compras"] + origen["ventas"]
    ):
        raise ValueError(f"Cobertura o volumen insuficientes: {origen}; días={estadistica['dias']}")
    if (
        cifras[0] <= 0
        or len(set(cifras)) != 1
        or saldos_mal
        or detalle_ventas != (origen["ventas"], cifras[0])
        or detalle_compras != origen["compras"]
    ):
        raise ValueError(f"No concilian la facturación ({cifras}) o el stock ({saldos_mal}).")

    resultado = {"filas_origen": origen, "controles": "aprobados", **indicadores}
    salida = base.parent / ".runtime" / "reporte_calidad.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return resultado


if __name__ == "__main__":
    print(json.dumps(reporte_calidad(), ensure_ascii=False, indent=2, default=str))
