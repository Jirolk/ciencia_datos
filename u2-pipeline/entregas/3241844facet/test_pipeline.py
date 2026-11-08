"""Pruebas unitarias para el pipeline de ingesta dlt enriquecido desde PokeAPI."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import dlt.extract.exceptions
import pytest
import requests
from pipeline import obtener_pokemon_api


def test_obtener_pokemon_api_estructura_enriquecida() -> None:
    """Prueba 1: Valida la extracción y estructuración de tipos, habilidades y movimientos."""
    mock_lista = MagicMock()
    mock_lista.json.return_value = {
        "next": None,
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon/1/",
            }
        ],
    }

    mock_detalle = MagicMock()
    mock_detalle.status_code = 200
    mock_detalle.json.return_value = {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "types": [{"type": {"name": "grass"}}],
        "abilities": [{"ability": {"name": "overgrow"}}],
        "moves": [{"move": {"name": "tackle"}}],
    }

    with (
        patch("requests.get", side_effect=[mock_lista, mock_detalle]),
        patch("time.sleep"),
    ):
        resultados = list(obtener_pokemon_api())
        assert len(resultados) == 1
        pokemon = resultados[0]
        assert pokemon["name"] == "bulbasaur"
        assert pokemon["tipos"] == json.dumps(["grass"])
        assert pokemon["habilidades"] == json.dumps(["overgrow"])
        assert pokemon["movimientos"] == json.dumps(["tackle"])


def test_obtener_pokemon_api_paginacion_multiple() -> None:
    """Prueba 2: Valida la extracción continua a través de múltiples páginas."""
    mock_pag1 = MagicMock()
    mock_pag1.json.return_value = {
        "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon/1/",
            }
        ],
    }

    mock_pag2 = MagicMock()
    mock_pag2.json.return_value = {
        "next": None,
        "results": [{"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"}],
    }

    mock_detalle = MagicMock()
    mock_detalle.status_code = 200
    mock_detalle.json.return_value = {
        "id": 1,
        "name": "poke",
        "types": [],
        "abilities": [],
        "moves": [],
    }

    with (
        patch(
            "requests.get",
            side_effect=[mock_pag1, mock_detalle, mock_pag2, mock_detalle],
        ),
        patch("time.sleep"),
    ):
        resultados = list(obtener_pokemon_api())
        assert len(resultados) == 2
        assert resultados[0]["name"] == "poke"
        assert resultados[1]["name"] == "poke"


def test_obtener_pokemon_api_cooldown_sleep_llamado() -> None:
    """Prueba 3: Comprueba la ejecución de las pausas de cooldown durante las peticiones."""
    mock_pag1 = MagicMock()
    mock_pag1.json.return_value = {
        "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon/1/",
            }
        ],
    }
    mock_pag2 = MagicMock()
    mock_pag2.json.return_value = {
        "next": None,
        "results": [],
    }
    mock_detalle = MagicMock()
    mock_detalle.status_code = 200
    mock_detalle.json.return_value = {
        "id": 1,
        "types": [],
        "abilities": [],
        "moves": [],
    }

    with (
        patch("requests.get", side_effect=[mock_pag1, mock_detalle, mock_pag2]),
        patch("time.sleep") as mock_sleep,
    ):
        list(obtener_pokemon_api())
        assert mock_sleep.called


def test_obtener_pokemon_api_caso_borde_respuesta_vacia() -> None:
    """Prueba 4 (Caso borde): Manejo de respuesta vacía o sin resultados."""
    mock_respuesta = MagicMock()
    mock_respuesta.json.return_value = {"next": None, "results": []}

    with patch("requests.get", return_value=mock_respuesta):
        resultados = list(obtener_pokemon_api())
        assert len(resultados) == 0


def test_obtener_pokemon_api_caso_borde_error_http_500() -> None:
    """Prueba 5 (Caso borde): Manejo de errores HTTP 500/404 via raise_for_status."""
    mock_respuesta = MagicMock()
    mock_respuesta.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

    with patch("requests.get", return_value=mock_respuesta):
        with pytest.raises(dlt.extract.exceptions.ResourceExtractionError):
            list(obtener_pokemon_api())


def test_obtener_pokemon_api_caso_borde_error_conexion() -> None:
    """Prueba 6 (Caso borde): Valida que dlt captura las fallas de red o timeouts."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Timeout de red"),
    ):
        with pytest.raises(dlt.extract.exceptions.ResourceExtractionError):
            list(obtener_pokemon_api())
