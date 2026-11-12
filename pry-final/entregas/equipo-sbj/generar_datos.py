"""Generador de datos sintéticos para un minimercado.

Produce cinco archivos CSV (productos, vendedores, compras, ventas y
movimientos_stock) coherentes entre sí y 100 % reproducibles: la misma
semilla (`--seed`) genera siempre exactamente los mismos archivos.

Se simula día a día el funcionamiento del local:
  1. Se registra el stock inicial de cada producto.
  2. Cada mañana se reponen (compra a proveedor) los productos cuyo stock cayó por debajo de su umbral.
  3. Se registran pequeñas mermas de productos perecederos.
  4. Se generan las ventas del día (la demanda varía por día de semana, por producto y tiene una leve tendencia de crecimiento).
Cada compra, venta y merma genera su movimiento de stock, por lo que el stock nunca queda negativo.

Uso:
    python generar_datos.py     # escribe en ./data
    python generar_datos.py --seed 7 --dias 120 --salida /tmp/datos
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
DIAS = 100  # Se exige un mínimo de 90 días
FECHA_INICIO = date(2026, 1, 1)  # la fecha de inicio es fija: no depende de la fecha de ejecución

# (nombre, categoria, costo_unitario, precio_venta, popularidad relativa)
CATALOGO = [
    ("Agua mineral 500ml", "Bebidas", 0.35, 0.70, 16),
    ("Gaseosa cola 2L", "Bebidas", 1.10, 1.90, 12),
    ("Jugo de naranja 1L", "Bebidas", 0.95, 1.70, 2),
    ("Cerveza lata 350ml", "Bebidas", 0.80, 1.50, 7),
    ("Leche entera 1L", "Lácteos", 0.85, 1.35, 12),
    ("Yogur natural 1L", "Lácteos", 1.00, 1.70, 4),
    ("Queso fresco 500g", "Lácteos", 3.20, 4.80, 1.2),
    ("Pan de molde", "Panadería", 1.10, 1.90, 11),
    ("Galletitas dulces", "Panadería", 0.60, 1.20, 6),
    ("Arroz 1kg", "Almacén", 0.90, 1.50, 5),
    ("Fideos 500g", "Almacén", 0.55, 1.00, 5),
    ("Aceite de girasol 900ml", "Almacén", 1.80, 2.90, 3),
    ("Azúcar 1kg", "Almacén", 0.80, 1.30, 3),
    ("Yerba mate 1kg", "Almacén", 2.50, 3.90, 3),
    ("Café molido 250g", "Almacén", 2.30, 3.80, 1.5),
    ("Detergente 750ml", "Limpieza", 1.20, 2.10, 1.5),
    ("Papel higiénico x4", "Limpieza", 1.50, 2.60, 2),
    ("Lavandina 1L", "Limpieza", 0.60, 1.10, 1),
    ("Papas fritas 150g", "Snacks", 1.00, 1.90, 4),
    ("Chocolate en tableta", "Snacks", 1.30, 2.40, 2.5),
]

PROVEEDORES = {
    "Bebidas": ["Distribuidora Río", "Bebidas del Sur"],
    "Lácteos": ["Lácteos La Pradera", "Granja Fresca"],
    "Panadería": ["Panificadora Central", "Dulces Hogar"],
    "Almacén": ["Mayorista Norte", "Almacenes Unidos"],
    "Limpieza": ["Limpiamax", "Mayorista Norte"],
    "Snacks": ["Distribuidora Río", "Snacks SA"],
}

# (nombre, sucursal, días de antigüedad respecto al inicio, peso de ventas)
VENDEDORES = [
    ("Ana Gómez", "Centro", 400, 1.3),
    ("Luis Benítez", "Centro", 250, 1.1),
    ("María Duarte", "Norte", 120, 1.0),
    ("Carlos Ramírez", "Norte", 30, 0.9),
    ("Sofía Villalba", "Centro", -25, 0.7),  # ingresa 25 días después del inicio
]

FACTOR_DIA_SEMANA = [0.85, 0.85, 0.90, 0.95, 1.20, 1.40, 1.10]  # lun..dom
PERECEDEROS = {"Lácteos", "Panadería"}

COLUMNAS = {
    "productos": ["id", "nombre", "categoria", "costo_unitario", "precio_venta", "stock_inicial"],
    "vendedores": ["id", "nombre", "sucursal", "fecha_alta"],
    "compras": ["id", "fecha", "producto_id", "cantidad", "costo_unitario", "proveedor"],
    "ventas": ["id", "fecha", "producto_id", "cantidad", "precio_unitario", "descuento", "vendedor_id"],
    "movimientos_stock": ["id", "fecha", "producto_id", "tipo", "cantidad", "motivo", "referencia_id"],
}


def generar(seed: int = SEED, dias: int = DIAS, fecha_inicio: date = FECHA_INICIO) -> dict[str, list[dict]]:
    """Simula la operación y devuelve las cinco tablas como listas de dicts."""
    if dias < 90:
        raise ValueError("El enunciado exige al menos 90 días de actividad.")
    rng = random.Random(seed)

    # --- Dimensiones ---
    productos = []
    for i, (nombre, cat, costo, precio, pop) in enumerate(CATALOGO, start=1):
        productos.append({
            "id": i, "nombre": nombre, "categoria": cat,
            "costo_unitario": costo, "precio_venta": precio,
            "stock_inicial": int(round(pop * 8 + rng.randint(10, 30))),
        })
    popularidad = {i: CATALOGO[i - 1][4] for i in range(1, len(CATALOGO) + 1)}

    vendedores = [
        {"id": i, "nombre": n, "sucursal": suc,
         "fecha_alta": (fecha_inicio - timedelta(days=antig)).isoformat()}
        for i, (n, suc, antig, _) in enumerate(VENDEDORES, start=1)
    ]
    peso_vendedor = {i: VENDEDORES[i - 1][3] for i in range(1, len(VENDEDORES) + 1)}

    compras: list[dict] = []
    ventas: list[dict] = []
    movs: list[dict] = []
    stock = {p["id"]: p["stock_inicial"] for p in productos}

    def mov(fecha, pid, tipo, cantidad, motivo, ref):
        movs.append({"id": len(movs) + 1, "fecha": fecha.isoformat(), "producto_id": pid,
                     "tipo": tipo, "cantidad": cantidad, "motivo": motivo,
                     "referencia_id": "" if ref is None else ref})

    # 1) Stock inicial
    for p in productos:
        mov(fecha_inicio, p["id"], "entrada", p["stock_inicial"], "stock_inicial", None)

    # --- Simulación diaria ---
    for d in range(dias):
        hoy = fecha_inicio + timedelta(days=d)
        dow = hoy.weekday()

        # 2) Reposición: umbral ≈ 4 días de demanda, lote ≈ 7 días de demanda
        for p in productos:
            pid = p["id"]
            umbral = math.ceil(popularidad[pid] * 1.7 + 2)
            if stock[pid] <= umbral:
                lote = math.ceil(popularidad[pid] * 3 + 8)
                costo = round(p["costo_unitario"] * rng.uniform(0.95, 1.05), 2)
                compras.append({
                    "id": len(compras) + 1, "fecha": hoy.isoformat(), "producto_id": pid,
                    "cantidad": lote, "costo_unitario": costo,
                    "proveedor": rng.choice(PROVEEDORES[p["categoria"]]),
                })
                stock[pid] += lote
                mov(hoy, pid, "entrada", lote, "compra", compras[-1]["id"])

        # 3) Mermas de perecederos (≈ 15 % de los días)
        if rng.random() < 0.15:
            perecederos = [p["id"] for p in productos if p["categoria"] in PERECEDEROS and stock[p["id"]] > 5]
            if perecederos:
                pid = rng.choice(perecederos)
                u = rng.randint(1, 3)
                stock[pid] -= u
                mov(hoy, pid, "salida", u, "merma", None)

        # 4) Ventas del día (demanda por día de semana + tendencia + ruido)
        media = 16 * FACTOR_DIA_SEMANA[dow] * (1 + 0.002 * d)
        n_ventas = max(5, int(round(rng.gauss(media, 2))))
        vend_activos = [v["id"] for v in vendedores if v["fecha_alta"] <= hoy.isoformat()]
        pesos_prod = []
        for p in productos:
            w = popularidad[p["id"]]
            if p["nombre"].startswith("Cerveza") and dow in (4, 5):
                w *= 1.8  # más cerveza los días viernes y sábado 
            pesos_prod.append(w)

        for _ in range(n_ventas):
            p = rng.choices(productos, weights=pesos_prod)[0]
            cantidad = rng.choices([1, 2, 3, 4, 5, 6], weights=[35, 28, 17, 10, 6, 4])[0]
            cantidad = min(cantidad, stock[p["id"]])
            if cantidad <= 0:
                continue  # venta perdida por quiebre de stock
            vid = rng.choices(vend_activos, weights=[peso_vendedor[v] for v in vend_activos])[0]
            descuento = rng.choices([0.0, 0.05, 0.10, 0.15], weights=[75, 12, 9, 4])[0]
            ventas.append({
                "id": len(ventas) + 1, "fecha": hoy.isoformat(), "producto_id": p["id"],
                "cantidad": cantidad, "precio_unitario": p["precio_venta"],
                "descuento": descuento, "vendedor_id": vid,
            })
            stock[p["id"]] -= cantidad
            mov(hoy, p["id"], "salida", cantidad, "venta", ventas[-1]["id"])

    datos = {"productos": productos, "vendedores": vendedores, "compras": compras,
             "ventas": ventas, "movimientos_stock": movs}
    validar(datos, dias)
    return datos


def validar(datos: dict[str, list[dict]], dias: int = DIAS) -> None:
    """Falla si los datos generados incumplen los requisitos del enunciado."""
    assert len(datos["productos"]) >= 20, "Se requieren 20 productos"
    assert len(datos["vendedores"]) >= 5, "Se requieren 5 vendedores"
    assert len(datos["compras"]) >= 100, f"Se requieren >=100 compras (hay {len(datos['compras'])})"
    assert len(datos["ventas"]) >= 500, f"Se requieren >=500 ventas (hay {len(datos['ventas'])})"

    pids = {p["id"] for p in datos["productos"]}
    vids = {v["id"] for v in datos["vendedores"]}
    assert all(v["producto_id"] in pids and v["vendedor_id"] in vids for v in datos["ventas"])
    assert all(c["producto_id"] in pids for c in datos["compras"])
    assert all(m["producto_id"] in pids for m in datos["movimientos_stock"])
    assert all(v["cantidad"] > 0 and v["precio_unitario"] > 0 and 0 <= v["descuento"] < 1 for v in datos["ventas"])
    assert all(c["cantidad"] > 0 and c["costo_unitario"] > 0 for c in datos["compras"])
    assert all(p["costo_unitario"] > 0 and p["precio_venta"] > p["costo_unitario"] for p in datos["productos"])

    # El stock acumulado nunca debe ser negativo
    saldo: dict[int, int] = {}
    for m in datos["movimientos_stock"]:
        signo = 1 if m["tipo"] == "entrada" else -1
        saldo[m["producto_id"]] = saldo.get(m["producto_id"], 0) + signo * m["cantidad"]
        assert saldo[m["producto_id"]] >= 0, f"Stock negativo en producto {m['producto_id']}"

    fechas = {v["fecha"] for v in datos["ventas"]}
    assert len(fechas) >= 90, f"Se requieren >=90 días con ventas (hay {len(fechas)})"


def escribir_csv(datos: dict[str, list[dict]], salida: Path) -> list[Path]:
    """Escribe una tabla por archivo CSV (UTF-8, saltos de línea LF)."""
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    rutas = []
    for tabla, filas in datos.items():
        ruta = salida / f"{tabla}.csv"
        with ruta.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS[tabla], lineterminator="\n")
            w.writeheader()
            w.writerows(filas)
        rutas.append(ruta)
    return rutas


def main(argv: list[str] | None = None) -> dict[str, int]:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=SEED, help="semilla aleatoria (default: 42)")
    ap.add_argument("--dias", type=int, default=DIAS, help="días de actividad (mínimo 90)")
    ap.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent / "data",
                    help="carpeta de salida (default: ./data)")
    args = ap.parse_args(argv)
    datos = generar(args.seed, args.dias)
    escribir_csv(datos, args.salida)
    resumen = {t: len(f) for t, f in datos.items()}
    print(f"Datos generados en {args.salida} (seed={args.seed}): {resumen}")
    return resumen


if __name__ == "__main__":
    main()
