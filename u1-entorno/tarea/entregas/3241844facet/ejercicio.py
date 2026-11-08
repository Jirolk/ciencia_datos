# Ejercicio de la tarea U1: este archivo tiene errores de estilo A PROPÓSITO.
# Cópialo a entregas/<tu-usuario>/ y corrígelo con ruff. Una de las advertencias
# esconde un error real: tus pruebas deberían poder detectarlo.
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
    resultado = round(precio * tasa, 2)
    return resultado


def resumen_por_marca(ventas, acumulado=None):
    """Suma el precio de venta por marca. Cada venta es un dict con 'car_make' y 'sale_price'."""
    if acumulado is None:
        acumulado = {}

    for v in ventas:
        marca = v["car_make"]
        acumulado[marca] = acumulado.get(marca, 0) + float(v["sale_price"])
    return acumulado


def descripcion_venta(venta):
    """Describe una venta en una línea."""
    mensaje = "Venta registrada"
    try:
        precio = float(venta["sale_price"])
    except ValueError:
        precio = 0
    return mensaje + ": " + venta["car_make"] + " " + venta["car_model"] + " por $" + str(precio)
