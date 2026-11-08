from datetime import date

from ejercicio import comision_esperada, parse_fecha, resumen_por_marca, separar_nombre_id


def test_comision_esperada():
    """Multiplica precio por tasa y redondea a dos decimales."""
    assert comision_esperada(30000, 0.02) == 600.0


def test_separar_nombre_id_con_id():
    """Separa el nombre del número final."""
    assert separar_nombre_id("Pedro Benítez 812") == ("Pedro Benítez", 812)


def test_parse_fecha_dia_bisiesto():
    """Caso borde: el 29 de febrero solo existe en años bisiestos."""
    assert parse_fecha("02/29/2028") == date(2028, 2, 29)


def test_resumen_por_marca_no_mezcla_llamadas():
    """Caso borde: una llamada nueva no arrastra las ventas de la anterior."""
    primera = resumen_por_marca([{"car_make": "Chevrolet", "sale_price": "22000"}])
    segunda = resumen_por_marca([{"car_make": "Mazda", "sale_price": "9500"}])

    assert primera == {"Chevrolet": 22000.0}
    assert segunda == {"Mazda": 9500.0}
