"""Pruebas unitarias para las funciones de ejercicio.py."""

from ejercicio import comision_esperada, resumen_por_marca


def test_comision_esperada_caso_tipico():
    """Prueba el cálculo de comisión con valores estándar."""
    precio = 1000.0
    tasa = 0.15
    resultado = comision_esperada(precio, tasa)
    assert resultado == 150.0


def test_resumen_por_marca_caso_borde_lista_vacia():
    """Caso borde: probar que una lista de ventas vacía retorna un diccionario vacío."""
    ventas = []
    resultado = resumen_por_marca(ventas)
    assert resultado == {}


def test_comision_esperada_caso_borde_cero():
    """Caso borde adicional: comisión con precio cero debe ser cero."""
    assert comision_esperada(0, 0.20) == 0.0
