"""Lee los CSV y reemplaza la foto completa de las cinco tablas de origen."""

import csv
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import dlt

from configuracion import TABLAS, carpeta_trabajo

TIPOS = {
    "productos": dict(
        id=int,
        nombre=str,
        categoria=str,
        costo_unitario=Decimal,
        precio_venta=Decimal,
        stock_inicial=int,
    ),
    "vendedores": dict(id=int, nombre=str, sucursal=str, fecha_alta=date.fromisoformat),
    "compras": dict(
        id=int,
        fecha=date.fromisoformat,
        producto_id=int,
        cantidad=int,
        costo_unitario=Decimal,
        proveedor=str,
    ),
    "ventas": dict(
        id=int,
        fecha=date.fromisoformat,
        producto_id=int,
        cantidad=int,
        precio_unitario=Decimal,
        descuento=Decimal,
        vendedor_id=int,
    ),
    "movimientos_stock": dict(
        id=int, fecha=date.fromisoformat, producto_id=int, tipo=str, referencia_id=int, cantidad=int
    ),
}


def leer_csv(carpeta, tabla):
    ruta = Path(carpeta) / f"{tabla}.csv"
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        tipos = TIPOS[tabla]
        if lector.fieldnames != list(tipos):
            raise ValueError(f"Columnas inesperadas en {ruta.name}: {lector.fieldnames}")
        filas = []
        ids = set()
        for numero, fila in enumerate(lector, 2):
            if None in fila or any(valor is None or not valor.strip() for valor in fila.values()):
                raise ValueError(f"Fila incompleta o mal formada: {ruta.name}:{numero}")
            registro = {campo: convertir(fila[campo]) for campo, convertir in tipos.items()}
            if registro["id"] < 1 or registro["id"] in ids:
                raise ValueError(f"ID inválido o repetido en {ruta.name}:{numero}")
            ids.add(registro["id"])
            filas.append(registro)
    if not filas:
        raise ValueError(f"{ruta.name} está vacío; se cancela la carga.")
    return filas


def ejecutar_ingesta(carpeta=None, base=None):
    trabajo = carpeta_trabajo()
    carpeta = Path(carpeta) if carpeta is not None else trabajo / "data"
    base = Path(base).resolve() if base is not None else trabajo / "data.duckdb"
    base.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("RUNTIME__DLTHUB_TELEMETRY", "false")
    instantanea = {tabla: leer_csv(carpeta, tabla) for tabla in TABLAS}
    recursos = [
        dlt.resource(filas, name=tabla, primary_key="id", write_disposition="replace")
        for tabla, filas in instantanea.items()
    ]
    flujo = dlt.pipeline(
        pipeline_name="minimercado",
        pipelines_dir=str(base.parent / ".runtime" / "dlt" / base.stem),
        destination=dlt.destinations.duckdb(str(base)),
        dataset_name="raw_minimercado",
    )
    carga = flujo.run(recursos)
    carga.raise_on_failed_jobs()
    return carga


if __name__ == "__main__":
    print(ejecutar_ingesta())
