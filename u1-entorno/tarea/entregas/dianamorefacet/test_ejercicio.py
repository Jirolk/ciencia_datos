from datetime import date

import pytest
from ejercicio import (
    comision_esperada,
    descripcion_venta,
    parse_fecha,
    resumen_por_marca,
    separar_nombre_id,
)


def test_parse_fecha():
    assert parse_fecha("12/25/2025") == date(2025, 12, 25)


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("Pedro Juan 1247", ("Pedro Juan", 1247)),
        ("Juan Perez 999", ("Juan Perez", 999)),
        ("Solo Nombre", ("Solo Nombre", None)),
        ("Cliente XYZ", ("Cliente XYZ", None)),
    ],
)
def test_separar_nombre_id(texto, esperado):
    assert separar_nombre_id(texto) == esperado


@pytest.mark.parametrize(
    "precio,tasa,resultado",
    [
        (1000, 0.10, 100.00),
        (199.99, 0.15, 30.00),
        (1234.56, 0.075, 92.59),
    ],
)
def test_comision_esperada(precio, tasa, resultado):
    assert comision_esperada(precio, tasa) == resultado


def test_resumen_por_marca():
    ventas = [
        {"car_make": "Ford", "sale_price": "10000"},
        {"car_make": "Ford", "sale_price": "5000"},
        {"car_make": "Toyota", "sale_price": "7500"},
    ]

    resultado = resumen_por_marca(ventas)

    assert resultado == {
        "Ford": 15000.0,
        "Toyota": 7500.0,
    }


def test_resumen_por_marca_multiples_llamadas_sin_acumulado():
    """
    Verifica que cada llamada que omite el parámetro
    acumulado utilice un diccionario nuevo.
    """
    r1 = resumen_por_marca([{"car_make": "Ford", "sale_price": "1000"}])

    r2 = resumen_por_marca([{"car_make": "Toyota", "sale_price": "2000"}])

    r3 = resumen_por_marca([{"car_make": "Ford", "sale_price": "3000"}])

    assert r1 == {"Ford": 1000.0}
    assert r2 == {"Toyota": 2000.0}
    assert r3 == {"Ford": 3000.0}


def test_resumen_por_marca_con_acumulado():
    acumulado = {"Ford": 1000.0}

    resultado = resumen_por_marca(
        [
            {"car_make": "Ford", "sale_price": "500"},
            {"car_make": "Toyota", "sale_price": "2000"},
        ],
        acumulado,
    )

    assert resultado == {
        "Ford": 1500.0,
        "Toyota": 2000.0,
    }


def test_descripcion_venta():
    venta = {
        "car_make": "Ford",
        "car_model": "Focus",
        "sale_price": "15000",
    }

    assert descripcion_venta(venta) == "Venta registrada: Ford Focus por $15000.0"


def test_descripcion_venta_precio_invalido():
    venta = {
        "car_make": "Ford",
        "car_model": "Focus",
        "sale_price": "abc",
    }

    assert descripcion_venta(venta) == "Venta registrada: Ford Focus por $0"
