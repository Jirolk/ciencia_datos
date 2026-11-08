from datetime import date

from ejercicio import (
    parse_fecha,
    resumen_por_marca,
    separar_nombre_id,
)


def test_parse_fecha_formato_americano():
    # Verifica la correcta conversión de cadenas en formato mes/día/año
    assert parse_fecha("12/25/2025") == date(2025, 12, 25)


def test_separar_nombre_y_codigo_con_identificador():
    # Comprueba la separación correcta cuando el texto contiene un número de ID
    nombre, codigo = separar_nombre_id("Carlos Ruiz 8889")
    assert nombre == "Carlos Ruiz"
    assert codigo == 8889




def test_resumen_por_marca_aislamiento_de_estado():
    # Asegura que las llamadas sucesivas no arrastren información anterior (estado mutable)
    primer_lote = [{"car_make": "Mazda", "sale_price": "200"}]
    segundo_lote = [{"car_make": "Chevrolet", "sale_price": "150"}]
    
    resumen_por_marca(primer_lote)
    resultado = resumen_por_marca(segundo_lote)
    
    assert resultado == {"Chevrolet": 150.0}


