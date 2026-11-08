"""Pruebas unitarias para el pipeline de ciudades de Paraguay con dlt."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pipeline
import pytest
import requests
from dlt.extract.exceptions import ResourceExtractionError


def test_estructura_recurso_dlt() -> None:
    """Valida la configuración del recurso dlt y la estructura de los datos extraídos."""
    datos_simulados = [
        {
            "geonameId": 3439389,
            "name": "Asunción",
            "asciiName": "Asuncion",
            "countryCode": "PY",
            "population": 1482200,
        },
        {
            "geonameId": 3437443,
            "name": "Concepción",
            "asciiName": "Concepcion",
            "countryCode": "PY",
            "population": 45068,
        },
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = datos_simulados
    mock_response.raise_for_status.return_value = None

    with patch("pipeline.requests.get", return_value=mock_response) as mock_get:
        recurso = pipeline.paraguay_cities_resource()
        resultados = list(recurso)

        mock_get.assert_called_once_with("https://countries.dev/cities?country=PY")
        assert recurso.name == "ciudades_py"
        assert len(resultados) == 2
        assert resultados[0]["name"] == "Asunción"
        assert resultados[0]["countryCode"] == "PY"
        assert "population" in resultados[0]


def test_caso_borde_respuesta_vacia() -> None:
    """Verifica que el recurso maneje correctamente una respuesta vacía de la API."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None

    with patch("pipeline.requests.get", return_value=mock_response):
        resultados = list(pipeline.paraguay_cities_resource())
        assert resultados == []


def test_caso_borde_error_conexion() -> None:
    """Verifica que un fallo de red en la API propague ResourceExtractionError en dlt."""
    with patch(
        "pipeline.requests.get",
        side_effect=requests.exceptions.ConnectionError("Error de conexión simulado"),
    ):
        with pytest.raises(ResourceExtractionError) as exc_info:
            list(pipeline.paraguay_cities_resource())

        assert isinstance(exc_info.value.__cause__, requests.exceptions.ConnectionError)
