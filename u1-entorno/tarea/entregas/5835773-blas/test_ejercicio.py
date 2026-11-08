"""Pruebas de ejercicio.py para la tarea U1."""

from ejercicio import parse_fecha, resumen_por_marca, separar_nombre_id


def test_parse_fecha_fecha_valida():
    assert parse_fecha("07/04/1776").isoformat() == "1776-07-04"


def test_separar_nombre_id_caso_borde_sin_numero():
    # Caso borde: texto sin ID al final -> devuelve el texto y None
    assert separar_nombre_id("Jennifer Thomas") == ("Jennifer Thomas", None)


def test_resumen_por_marca_no_contamina_entre_llamadas():
    # El dict por defecto no debe recordar ventas de llamadas anteriores
    primero = resumen_por_marca([{"car_make": "Ford", "sale_price": 1000}])
    segundo = resumen_por_marca([{"car_make": "Toyota", "sale_price": 500}])
    assert primero == {"Ford": 1000.0}
    assert segundo == {"Toyota": 500.0}
