"""Repite las comprobaciones y guarda evidencias sin depender del editor."""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from zoneinfo import ZoneInfo

from pipeline import CARPETA, ejecutar_pipeline
from verificar_datos import verificar_datos


def main():
    controles = {}
    for nombre, argumentos in (
        ("ruff", ["ruff", "check", "."]),
        ("formato", ["ruff", "format", "--check", "."]),
        ("pytest", ["pytest", "test_pipeline.py", "-q"]),
    ):
        resultado = subprocess.run(
            [sys.executable, "-m", *argumentos],
            cwd=CARPETA,
            capture_output=True,
            text=True,
            check=False,
        )
        salida = resultado.stdout + resultado.stderr
        print(f"[{nombre}]\n{salida}", flush=True)
        if resultado.returncode:
            raise RuntimeError(f"Falló la comprobación {nombre}.")
        controles[nombre] = salida.strip()

    print(ejecutar_pipeline(), flush=True)
    datos = verificar_datos()
    evidencia = {
        "fecha": datetime.now(ZoneInfo("America/Asuncion")).isoformat(),
        "sistema": platform.system(),
        "codespaces": os.environ.get("CODESPACES") == "true",
        "contenedor": Path("/.dockerenv").exists(),
        "python": platform.python_version(),
        "versiones": {nombre: version(nombre) for nombre in ("dlt", "duckdb", "pytest", "ruff")},
        "controles": controles,
        "datos": datos,
    }
    destino = CARPETA / "evidencias.json"
    destino.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Total confirmado con SQL: {datos['total']}", flush=True)
    print(f"Evidencias guardadas en {destino}", flush=True)


if __name__ == "__main__":
    main()
