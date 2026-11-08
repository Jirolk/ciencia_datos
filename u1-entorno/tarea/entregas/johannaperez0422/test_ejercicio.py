from ejercicio import comision_esperada, resumen_por_marca


def test_comision_redondeada():
    assert comision_esperada(123.45, 0.07) == 8.64


def test_resumen_suma_por_marca():
    ventas = [
        {"car_make": "Toyota", "sale_price": "100"},
        {"car_make": "Toyota", "sale_price": "50"},
        {"car_make": "Ford", "sale_price": "80"},
    ]

    resultado = resumen_por_marca(ventas)

    assert resultado == {"Toyota": 150.0, "Ford": 80.0}


def test_resumen_lista_vacia():
    assert resumen_por_marca([]) == {}


def test_resumen_llamadas_independientes():
    primero = resumen_por_marca([{"car_make": "Toyota", "sale_price": "100"}])
    segundo = resumen_por_marca([{"car_make": "Ford", "sale_price": "80"}])

    assert primero == {"Toyota": 100.0}
    assert segundo == {"Ford": 80.0}
