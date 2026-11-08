from datetime import date

from ejercicio import parse_fecha, resumen_por_marca, separar_nombre_id


def test_parse_fecha_acepta_un_dia_bisiesto():
    assert parse_fecha("02/29/2024") == date(2024, 2, 29)


def test_separar_nombre_id_si_no_hay_id_devuelve_none():
    assert separar_nombre_id("Jennifer Thomas") == ("Jennifer Thomas", None)


def test_resumen_por_marca_no_comparte_datos_entre_llamadas():
    ventas = [{"car_make": "Toyota", "sale_price": "12000"}]

    assert resumen_por_marca(ventas) == {"Toyota": 12000.0}
    assert resumen_por_marca(ventas) == {"Toyota": 12000.0}
