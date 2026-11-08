from ejercicio import comision_esperada, resumen_por_marca, separar_nombre_id


def test_comision_esperada_caso_normal():
    assert comision_esperada(1000, 0.1) == 100.0


def test_separar_nombre_id_sin_id_caso_borde():
    assert separar_nombre_id("  Jennifer Thomas  ") == ("Jennifer Thomas", None)


def test_resumen_por_marca_no_acumula_entre_llamadas():
    primera = resumen_por_marca([{"car_make": "Toyota", "sale_price": "1000"}])
    segunda = resumen_por_marca([{"car_make": "Honda", "sale_price": "2000"}])
    assert primera == {"Toyota": 1000.0}
    assert segunda == {"Honda": 2000.0}
