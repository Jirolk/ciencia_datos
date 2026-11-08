from ejercicio import (
    comision_esperada,
    descripcion_venta,
    resumen_por_marca,
    separar_nombre_id,
)


# -------------------------------------------------------------------
# Prueba 1: Caso normal (Happy path)
# -------------------------------------------------------------------
def test_separar_nombre_id_caso_normal():
    """Prueba el funcionamiento estándar con un nombre y un ID válido."""
    nombre, usuario_id = separar_nombre_id("Juan Gonzalez 1247")

    assert nombre == "Juan Gonzalez"
    assert usuario_id == 1247


def test_comision_esperada_normal():
    """Verifica el cálculo de la comisión con redondos a 2 decimales."""
    resultado = comision_esperada(100.0, 0.15)
    assert resultado == 15.0


# -------------------------------------------------------------------
# Prueba 2: Caso borde (Edge case)
# -------------------------------------------------------------------
def test_separar_nombre_id_sin_numero():
    """
    Caso borde: Texto de entrada que no contiene un ID al final.
    Debe retornar el texto limpio y None como ID.
    """
    nombre, usuario_id = separar_nombre_id("  Juan Perez  ")

    assert nombre == "Juan Perez"
    assert usuario_id is None


def test_resumen_por_marca_lista_vacia():
    """
    Caso borde: Pasar una lista vacía de ventas.
    Debe retornar un diccionario vacío sin fallar.
    """
    resultado = resumen_por_marca([])
    assert resultado == {}


def test_descripcion_venta_precio_invalido():
    """
    Caso borde: 'sale_price' no es convertible a float.
    El try-except debe manejarlo asignando precio = 0.
    """
    venta = {"car_make": "Toyota", "car_model": "Corolla", "sale_price": "No disponible"}
    resultado = descripcion_venta(venta)
    assert resultado == "Venta registrada: Toyota Corolla por $0"
