import re
from datetime import datetime


def parse_fecha(texto):
    """Convierte 'MM/DD/YYYY' en un objeto date."""
    return datetime.strptime(texto, "%m/%d/%Y").date()


def separar_nombre_id(texto):
    """Separa 'Jennifer Thomas 1247' en ('Jennifer Thomas', 1247)."""
    m = re.match(r"^(.*?)\s+(\d+)$", texto.strip())
    if m is None:
        return (texto.strip(), None)
    return (m.group(1), int(m.group(2)))


def comision_esperada(precio, tasa):
    """Comisión = precio por tasa, redondeada a dos decimales."""
    return round(precio * tasa, 2)


def resumen_por_marca(ventas, acumulado=None):
    """Suma el precio de venta por marca."""
    if acumulado is None:
        acumulado = {}

    for venta in ventas:
        marca = venta["car_make"]
        acumulado[marca] = acumulado.get(marca, 0) + float(venta["sale_price"])
    return acumulado


def descripcion_venta(venta):
    """Describe una venta en una línea."""
    try:
        precio = float(venta["sale_price"])
    except (KeyError, TypeError, ValueError):
        precio = 0

    return f"Venta registrada: {venta['car_make']} {venta['car_model']} por ${precio}"
