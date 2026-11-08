"""Pruebas de ejercicio.py (tarea U1)."""

from datetime import date

import pytest
from ejercicio import (
    comision_esperada,
    descripcion_venta,
    parse_fecha,
    resumen_por_marca,
    separar_nombre_id,
)


def test_parse_fecha_convierte_formato_estadounidense():
    assert parse_fecha("03/15/2022") == date(2022, 3, 15)


def test_parse_fecha_rechaza_mes_invalido():
    # Caso borde: "13" no es un mes válido.
    with pytest.raises(ValueError):
        parse_fecha("13/01/2022")


def test_separar_nombre_id_caso_normal():
    assert separar_nombre_id("Jennifer Thomas 1247") == ("Jennifer Thomas", 1247)


def test_separar_nombre_id_sin_numero():
    # Caso borde: sin identificador al final, devuelve None como id.
    assert separar_nombre_id("  Jennifer Thomas  ") == ("Jennifer Thomas", None)


def test_comision_esperada_redondea_a_dos_decimales():
    assert comision_esperada(15983.0, 0.0723) == 1155.57


def test_resumen_por_marca_suma_por_marca():
    ventas = [
        {"car_make": "Ford", "sale_price": "1000"},
        {"car_make": "Ford", "sale_price": "500.5"},
        {"car_make": "Honda", "sale_price": "200"},
    ]
    assert resumen_por_marca(ventas) == {"Ford": 1500.5, "Honda": 200.0}


def test_resumen_por_marca_no_arrastra_llamadas_anteriores():
    # Caso borde: dos llamadas independientes no deben compartir el acumulado.
    resumen_por_marca([{"car_make": "Ford", "sale_price": "1000"}])
    segundo = resumen_por_marca([{"car_make": "Ford", "sale_price": "1"}])
    assert segundo == {"Ford": 1.0}


def test_resumen_por_marca_lista_vacia():
    # Caso borde: sin ventas, el resumen está vacío.
    assert resumen_por_marca([]) == {}


def test_descripcion_venta_con_precio_invalido_usa_cero():
    venta = {"car_make": "Toyota", "car_model": "Corolla", "sale_price": "N/A"}
    assert descripcion_venta(venta) == "Venta registrada: Toyota Corolla por $0"
