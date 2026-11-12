"""Ejecuta dbt build con un perfil local y devuelve el resultado de la corrida."""

import json
import os
import subprocess
import sys
from pathlib import Path

from configuracion import PROYECTO, carpeta_trabajo


def ejecutar_dbt(base=None):
    trabajo = carpeta_trabajo()
    base = Path(base).resolve() if base is not None else trabajo / "data.duckdb"
    if not base.is_file():
        raise FileNotFoundError(f"Falta la base de ingesta: {base}")
    proyecto_dbt = PROYECTO / "dbt_project"
    corrida = base.parent / ".runtime" / "dbt" / base.stem
    ejecutable = Path(sys.executable).with_name("dbt.exe" if os.name == "nt" else "dbt")
    ambiente = {
        **os.environ,
        "MINIMERCADO_DB": str(base),
        "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
        "DBT_USE_COLORS": "false",
    }
    subprocess.run(
        [
            str(ejecutable),
            "build",
            "--project-dir",
            str(proyecto_dbt),
            "--profiles-dir",
            str(proyecto_dbt),
            "--target-path",
            str(corrida / "target"),
            "--log-path",
            str(corrida / "logs"),
        ],
        cwd=PROYECTO,
        env=ambiente,
        check=True,
    )
    resultados = json.loads((corrida / "target" / "run_results.json").read_text(encoding="utf-8"))
    return {
        "modelos": sum(r["status"] == "success" for r in resultados["results"]),
        "pruebas_dbt": sum(r["status"] == "pass" for r in resultados["results"]),
    }


if __name__ == "__main__":
    print(ejecutar_dbt())
