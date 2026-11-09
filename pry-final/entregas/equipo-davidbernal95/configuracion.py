"""Ubicaciones compartidas por los scripts, dbt y Dagster."""

import os
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent
TABLAS = ("productos", "vendedores", "compras", "ventas", "movimientos_stock")


def carpeta_trabajo():
    return Path(os.environ.get("MINIMERCADO_WORKDIR", PROYECTO)).resolve()
