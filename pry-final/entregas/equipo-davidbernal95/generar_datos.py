"""Genera un historial determinista de compras, ventas y movimientos."""

import argparse
import csv
from datetime import date, timedelta
from pathlib import Path
from random import Random

from configuracion import carpeta_trabajo

SEMILLA = 2026
DIAS = 90
INICIO = date(2026, 1, 1)
VENDEDORES = ("Fabricio Díaz", "Camila Benítez", "Matías Rojas", "Lucía Fernández", "Diego Acosta")
PROVEEDORES = (
    "Distribuidora Central",
    "Alimentos del Sur",
    "Comercial San Miguel",
    "Mayorista Horizonte",
)
CATALOGO = (
    ("Arroz", "Despensa", 5200),
    ("Fideos", "Despensa", 4100),
    ("Aceite", "Despensa", 11200),
    ("Harina", "Despensa", 4600),
    ("Azúcar", "Despensa", 5400),
    ("Yerba", "Despensa", 10800),
    ("Sal", "Despensa", 2100),
    ("Lentejas", "Despensa", 8300),
    ("Leche", "Bebidas", 5900),
    ("Agua", "Bebidas", 2500),
    ("Jugo", "Bebidas", 6300),
    ("Gaseosa", "Bebidas", 7800),
    ("Galletitas", "Alimentos", 3200),
    ("Pan lactal", "Alimentos", 8700),
    ("Atún", "Alimentos", 9800),
    ("Puré de tomate", "Alimentos", 3800),
    ("Detergente", "Limpieza", 6700),
    ("Jabón", "Limpieza", 3400),
    ("Papel higiénico", "Limpieza", 9400),
    ("Esponja", "Limpieza", 1900),
)


def generar_datos(destino=None, *, seed=SEMILLA, dias=DIAS):
    """Escribe los cinco CSV y devuelve el número de filas de cada uno."""
    if dias < DIAS:
        raise ValueError(f"La simulación requiere al menos {DIAS} días.")
    destino = Path(destino) if destino is not None else carpeta_trabajo() / "data"
    destino.mkdir(parents=True, exist_ok=True)
    rng = Random(seed)
    productos = [
        {
            "id": id_,
            "nombre": nombre,
            "categoria": categoria,
            "costo_unitario": costo,
            "precio_venta": (costo * rng.randint(126, 154) + 4999) // 5000 * 50,
            "stock_inicial": rng.randint(28, 55),
        }
        for id_, (nombre, categoria, costo) in enumerate(CATALOGO, 1)
    ]
    vendedores = [
        {
            "id": id_,
            "nombre": VENDEDORES[id_ - 1],
            "sucursal": "Centro",
            "fecha_alta": (INICIO - timedelta(days=rng.randint(40, 300))).isoformat(),
        }
        for id_ in range(1, 6)
    ]
    compras, ventas, movimientos = [], [], []
    stock = {p["id"]: p["stock_inicial"] for p in productos}

    def mover(fecha, producto_id, cantidad, tipo, referencia_id):
        stock[producto_id] += cantidad if tipo == "entrada" else -cantidad
        movimientos.append(
            {
                "id": len(movimientos) + 1,
                "fecha": fecha,
                "producto_id": producto_id,
                "tipo": tipo,
                "referencia_id": referencia_id,
                "cantidad": cantidad,
            }
        )

    for dia in range(dias):
        fecha = INICIO + timedelta(days=dia)
        fecha_iso = fecha.isoformat()
        # Se reciben compras antes de vender; hay una segunda entrega cada cinco días.
        for indice in range(1 + (dia % 5 == 0)):
            producto = productos[(dia * 7 + indice * 9) % len(productos)]
            id_ = len(compras) + 1
            cantidad = rng.randint(8, 23)
            costo = (producto["costo_unitario"] * rng.randint(90, 115) + 50) // 100
            compras.append(
                {
                    "id": id_,
                    "fecha": fecha_iso,
                    "producto_id": producto["id"],
                    "cantidad": cantidad,
                    "costo_unitario": costo,
                    "proveedor": PROVEEDORES[rng.randint(1, 4) - 1],
                }
            )
            mover(fecha_iso, producto["id"], cantidad, "entrada", id_)

        cantidad_ventas = rng.randint(6, 10) + (3 if fecha.weekday() >= 5 else 0)
        for _ in range(cantidad_ventas):
            disponibles = [p for p in productos if stock[p["id"]] > 0]
            if not disponibles:
                raise RuntimeError(f"Stock agotado para todo el catálogo el {fecha_iso}.")
            pesos = [2 + (21 - p["id"]) ** 2 for p in disponibles]
            producto = rng.choices(disponibles, weights=pesos, k=1)[0]
            cantidad = min(stock[producto["id"]], rng.randint(1, 4))
            id_ = len(ventas) + 1
            ventas.append(
                {
                    "id": id_,
                    "fecha": fecha_iso,
                    "producto_id": producto["id"],
                    "cantidad": cantidad,
                    "precio_unitario": producto["precio_venta"],
                    "descuento": rng.choices(
                        ["0.00", "0.05", "0.10", "0.15"],
                        weights=[75, 10, 10, 5],
                        k=1,
                    )[0],
                    "vendedor_id": rng.choices(range(1, 6), weights=[25, 23, 20, 17, 15], k=1)[0],
                }
            )
            mover(fecha_iso, producto["id"], cantidad, "salida", id_)

    tablas = {
        "productos": productos,
        "vendedores": vendedores,
        "compras": compras,
        "ventas": ventas,
        "movimientos_stock": movimientos,
    }
    for nombre, filas in tablas.items():
        with (destino / f"{nombre}.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
    return {nombre: len(filas) for nombre, filas in tablas.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEMILLA)
    parser.add_argument("--dias", type=int, default=DIAS)
    opciones = parser.parse_args()
    print(generar_datos(seed=opciones.seed, dias=opciones.dias))
