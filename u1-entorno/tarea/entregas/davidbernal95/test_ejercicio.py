from ejercicio import resumen_por_marca


def test_suma_ventas_de_la_misma_marca():
    ventas = [
        {"car_make": "Toyota", "sale_price": "100"},
        {"car_make": "Toyota", "sale_price": "50"},
        {"car_make": "Ford", "sale_price": "80"},
    ]

    assert resumen_por_marca(ventas) == {"Toyota": 150.0, "Ford": 80.0}


def test_lista_vacia():
    assert resumen_por_marca([]) == {}


def test_llamadas_independientes():
    resumen_por_marca([{"car_make": "Toyota", "sale_price": "100"}])

    resultado = resumen_por_marca([{"car_make": "Ford", "sale_price": "80"}])

    assert resultado == {"Ford": 80.0}
