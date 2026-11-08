"""Genera datos sintéticos de un minimercado y los guarda como CSV en data/.
Con la misma semilla siempre salen exactamente los mismos datos.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 42
FECHA_INICIO = date(2026, 7, 1)
DIAS = 120
DIR_DATA = Path(__file__).parent / "data"

PUNTO_REPOSICION = 25  # si el stock baja de esto, se compra mercadería
PROVEEDORES = {
    "bebidas": "Distribuidora Guaraní",
    "lácteos": "Lácteos del Este",
    "limpieza": "Importadora Sur",
    "snacks": "Mayorista Central",
}

# (nombre, categoría, costo_unitario, precio_venta, stock_inicial, peso_de_demanda)
# El peso hace que unos productos ("estrella") se vendan mucho más que otros.
CATALOGO = [
    ("Agua mineral 1,5 L", "bebidas", 3500, 5000, 120, 10),
    ("Gaseosa cola 2 L", "bebidas", 9000, 13000, 100, 12),
    ("Jugo de naranja 1 L", "bebidas", 7000, 10000, 70, 4),
    ("Cerveza lata 350 ml", "bebidas", 6500, 9500, 100, 6),
    ("Yerba mate 500 g", "bebidas", 14000, 19000, 80, 9),
    ("Leche entera 1 L", "lácteos", 6500, 8500, 120, 11),
    ("Yogur de frutilla 1 L", "lácteos", 8000, 11500, 60, 3),
    ("Queso paraguay 500 g", "lácteos", 22000, 30000, 40, 3),
    ("Manteca 200 g", "lácteos", 9000, 12500, 50, 2),
    ("Crema de leche 200 ml", "lácteos", 5000, 7500, 50, 2),
    ("Detergente 750 ml", "limpieza", 8000, 11500, 60, 3),
    ("Lavandina 1 L", "limpieza", 4500, 6500, 60, 3),
    ("Jabón en polvo 1 kg", "limpieza", 16000, 22000, 50, 3),
    ("Papel higiénico x4", "limpieza", 12000, 17000, 100, 6),
    ("Esponja x3", "limpieza", 3500, 5500, 60, 2),
    ("Papas fritas 150 g", "snacks", 9500, 13500, 80, 5),
    ("Galletitas dulces 300 g", "snacks", 5000, 7500, 100, 5),
    ("Chocolate en barra", "snacks", 6000, 9000, 90, 4),
    ("Maní salado 200 g", "snacks", 5500, 8000, 60, 2),
    ("Alfajor", "snacks", 3500, 5500, 110, 6),
]

VENDEDORES = [
    ("Ana Benítez", "Centro"),
    ("Carlos Gómez", "Centro"),
    ("Lucía Martínez", "Norte"),
    ("Diego Ramírez", "Norte"),
    ("Sofía Acosta", "Sur"),
]


def generar_productos() -> list[dict]:
    return [
        {
            "id": i,
            "nombre": nombre,
            "categoria": categoria,
            "costo_unitario": costo,
            "precio_venta": precio,
            "stock_inicial": stock,
        }
        for i, (nombre, categoria, costo, precio, stock, _peso) in enumerate(CATALOGO, start=1)
    ]


def generar_vendedores(rng: random.Random) -> list[dict]:
    return [
        {
            "id": i,
            "nombre": nombre,
            "sucursal": sucursal,
            "fecha_alta": (FECHA_INICIO - timedelta(days=rng.randint(30, 700))).isoformat(),
        }
        for i, (nombre, sucursal) in enumerate(VENDEDORES, start=1)
    ]


def generar_transacciones(
    rng: random.Random, productos: list[dict]
) -> tuple[list[dict], list[dict], list[dict]]:
    """Simula día por día compras, ventas y movimientos de stock sin dejar stock negativo."""
    stock = {p["id"]: p["stock_inicial"] for p in productos}
    pesos = [fila[5] for fila in CATALOGO]
    ids = [p["id"] for p in productos]
    por_id = {p["id"]: p for p in productos}

    compras: list[dict] = []
    ventas: list[dict] = []
    movimientos: list[dict] = []

    def registrar_compra(dia: date, producto_id: int, cantidad: int) -> None:
        producto = por_id[producto_id]
        costo = round(producto["costo_unitario"] * rng.uniform(0.95, 1.05))
        compra = {
            "id": len(compras) + 1,
            "fecha": dia.isoformat(),
            "producto_id": producto_id,
            "cantidad": cantidad,
            "costo_unitario": costo,
            "proveedor": PROVEEDORES[producto["categoria"]],
        }
        compras.append(compra)
        stock[producto_id] += cantidad
        movimientos.append(
            {
                "id": len(movimientos) + 1,
                "fecha": dia.isoformat(),
                "producto_id": producto_id,
                "tipo": "entrada",
                "cantidad": cantidad,
                "referencia": f"compra-{compra['id']}",
            }
        )

    for n in range(DIAS):
        dia = FECHA_INICIO + timedelta(days=n)

        # 1) Llega mercadería: reposición por stock bajo y un pedido semanal los lunes.
        for producto_id in ids:
            if stock[producto_id] < PUNTO_REPOSICION:
                registrar_compra(dia, producto_id, rng.randint(8, 15))
        if dia.weekday() == 0:
            for producto_id in rng.sample(ids, 5):
                registrar_compra(dia, producto_id, rng.randint(8, 15))

        # 2) Ventas del día: más movimiento los fines de semana.
        media = 9 if dia.weekday() >= 5 else 6
        for _ in range(max(1, round(rng.gauss(media, 1.5)))):
            producto_id = rng.choices(ids, weights=pesos)[0]
            cantidad = min(rng.choices([1, 2, 3, 4, 5], [45, 25, 15, 10, 5])[0], stock[producto_id])
            if cantidad == 0:
                continue  # sin stock no se vende
            venta = {
                "id": len(ventas) + 1,
                "fecha": dia.isoformat(),
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio_unitario": por_id[producto_id]["precio_venta"],
                "descuento": rng.choices([0.0, 0.05, 0.10, 0.15], [70, 15, 10, 5])[0],
                "vendedor_id": rng.randint(1, len(VENDEDORES)),
            }
            ventas.append(venta)
            stock[producto_id] -= cantidad
            movimientos.append(
                {
                    "id": len(movimientos) + 1,
                    "fecha": dia.isoformat(),
                    "producto_id": producto_id,
                    "tipo": "salida",
                    "cantidad": cantidad,
                    "referencia": f"venta-{venta['id']}",
                }
            )

    return compras, ventas, movimientos


def generar(semilla: int = SEMILLA) -> dict[str, list[dict]]:
    """Devuelve todas las tablas en memoria. Misma semilla, mismos datos."""
    rng = random.Random(semilla)
    productos = generar_productos()
    vendedores = generar_vendedores(rng)
    compras, ventas, movimientos = generar_transacciones(rng, productos)
    return {
        "productos": productos,
        "vendedores": vendedores,
        "compras": compras,
        "ventas": ventas,
        "movimientos_stock": movimientos,
    }


def escribir_csv(datos: dict[str, list[dict]], directorio: Path = DIR_DATA) -> None:
    directorio.mkdir(parents=True, exist_ok=True)
    for nombre, filas in datos.items():
        with open(directorio / f"{nombre}.csv", "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
            escritor.writeheader()
            escritor.writerows(filas)


def main() -> None:
    datos = generar()
    escribir_csv(datos)
    for nombre, filas in datos.items():
        print(f"{nombre}: {len(filas)} filas")


if __name__ == "__main__":
    main()
