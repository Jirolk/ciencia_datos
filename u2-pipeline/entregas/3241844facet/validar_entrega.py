"""Revisa los requisitos formales de una entrega de la tarea U1.

Uso (desde la raíz del repositorio):
    python u1-entorno/tarea/validar_entrega.py --usuario <usuario> --base origin/main

Comprueba: carpeta propia, número de commits, informe y pruebas. El estilo y las
pruebas se ejecutan aparte (ruff y pytest). Termina con código 1 si algo falla.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RAIZ_ENTREGAS = "u2-pipeline/entregas"
MIN_COMMITS = 3
MIN_PALABRAS = 500
MAX_PALABRAS = 700
MIN_PRUEBAS = 2
SECCIONES = ["Entorno", "Flujo de Git", "Un problema", "Reflexión", "Ayudas externas"]


def fuera_de_carpeta(archivos: list[str], usuario: str) -> list[str]:
    """Devuelve los archivos que no están dentro de la carpeta de la persona."""
    prefijo = f"{RAIZ_ENTREGAS}/{usuario}/".lower()
    return [a for a in archivos if not a.lower().startswith(prefijo)]


def contar_palabras(markdown: str) -> int:
    """Cuenta palabras sin comentarios HTML ni bloques de código."""
    texto = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    texto = re.sub(r"```.*?```", " ", texto, flags=re.DOTALL)
    return len(re.findall(r"\w+", texto))


def secciones_faltantes(markdown: str) -> list[str]:
    """Devuelve las secciones obligatorias que no aparecen como encabezado."""
    encabezados = [
        linea.lstrip("#").strip().lower()
        for linea in markdown.splitlines()
        if linea.startswith("#")
    ]
    return [s for s in SECCIONES if not any(e.startswith(s.lower()) for e in encabezados)]


def contar_pruebas(codigo: str) -> int:
    """Cuenta las funciones de prueba (def test_...) de un archivo."""
    return len(re.findall(r"^def test_\w+", codigo, flags=re.MULTILINE))


def _git(*argumentos: str) -> str:
    resultado = subprocess.run(["git", *argumentos], capture_output=True, text=True, check=True)
    return resultado.stdout.strip()


def revisar(usuario: str, base: str, raiz: Path) -> list[tuple[bool, str]]:
    """Ejecuta todas las comprobaciones y devuelve (cumple, mensaje)."""
    resultados: list[tuple[bool, str]] = []
    carpeta = raiz / RAIZ_ENTREGAS / usuario

    cambiados = _git("diff", "--name-only", f"{base}...HEAD").splitlines()
    ajenos = fuera_de_carpeta(cambiados, usuario)
    solo_mi_carpeta = bool(cambiados) and not ajenos
    if solo_mi_carpeta:
        resultados.append((True, "El PR toca solo tu carpeta"))
    elif ajenos:
        resultados.append((False, f"El PR toca archivos ajenos: {ajenos}"))
    else:
        resultados.append((False, "El PR no cambia ningún archivo"))

    commits = int(_git("rev-list", "--count", "--no-merges", f"{base}..HEAD"))
    resultados.append((commits >= MIN_COMMITS, f"Commits: {commits} (mínimo {MIN_COMMITS})"))

    informe = carpeta / "informe.md"
    if informe.exists():
        texto = informe.read_text(encoding="utf-8")
        palabras = contar_palabras(texto)
        resultados.append(
            (
                MIN_PALABRAS <= palabras <= MAX_PALABRAS,
                f"Informe: {palabras} palabras ({MIN_PALABRAS} a {MAX_PALABRAS})",
            )
        )
        faltan = secciones_faltantes(texto)
        if faltan:
            resultados.append((False, f"Faltan secciones en el informe: {faltan}"))
        else:
            resultados.append((True, "Informe con todas las secciones"))
    else:
        resultados.append((False, "Falta informe.md"))

    for nombre in ("pipeline.py", "test_pipeline.py", "verificar_datos.py"):
        resultados.append(((carpeta / nombre).exists(), f"Existe {nombre}"))

    pruebas = carpeta / "test_ejercicio.py"
    if pruebas.exists():
        n = contar_pruebas(pruebas.read_text(encoding="utf-8"))
        resultados.append((n >= MIN_PRUEBAS, f"Pruebas: {n} (mínimo {MIN_PRUEBAS})"))

    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usuario", required=True)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--raiz", default=".")
    args = parser.parse_args()

    resultados = revisar(args.usuario, args.base, Path(args.raiz))
    for cumple, mensaje in resultados:
        print(f"[{'OK' if cumple else 'FALLA'}] {mensaje}")
    return 0 if all(cumple for cumple, _ in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
