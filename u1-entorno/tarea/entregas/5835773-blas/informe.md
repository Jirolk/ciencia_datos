cat > u1-entorno/tarea/entregas/5835773-blas/informe.md << 'EOF'
# Informe de unidad 1

**Nombre:** Blas Antonio Zavala
**Fecha:** 18 de octubre de 2026
**Tag de cierre:** `u1-completa`

## Entorno

Trabajé en un Codespace, el entorno de desarrollo que GitHub abre en el navegador sobre un contenedor Docker. No instalé Python ni git en mi computadora.

El repositorio trae un archivo `.devcontainer` que, al crearse el Codespace, ejecuta `uv sync --all-groups` y prepara el entorno virtual. Antes de tocar código lo activé con `source .venv/bin/activate`, y el prompt mostró `(curso-analisis-datos)`.

Después ejecuté `python u1-entorno/tarea/verificar_entorno.py`, que revisa la versión mínima de Python, git y las herramientas del curso. Uso Python 3.12.11, pytest 9.1.1 y ruff 0.16.10.

La primera verificación falló: dijo que `pre-commit` NO ENCONTRADO. Lo instalé con `uv pip install pre-commit` y la segunda vez todo salió OK. Sin un entorno verificado, el trabajo no se puede reproducir.

## Flujo de Git

Empecé haciendo un fork de `ubuntumb/ciencia_datos` a mi cuenta, una copia propia donde puedo probar sin romper el repositorio del curso.

Dentro del Codespace creé la rama con `git switch -c u1/5835773-blas`. Vi que `uv.lock` aparecía modificado por la instalación del entorno, así que lo restauré con `git restore uv.lock`: el pull request solo debe tocar mi carpeta.

Hice cuatro commits pequeños en lugar de uno grande:

- La corrección de estilo que pide la guía.
- El bug real, junto con las pruebas que lo detectan.
- El informe.
- Su ampliación hasta el rango pedido.

Los commits cortos, con mensajes que explican el porqué, permiten revisar cada decisión por separado y volver atrás sin perder el resto. Entrego con un pull request hacia `main` del repositorio del curso.

## Un problema que apareció

El más interesante no lo encontró ruff sino una prueba. La función `resumen_por_marca` tenía `acumulado={}` como valor por defecto. Python crea ese diccionario una sola vez, al definir la función, y lo reutiliza en todas las llamadas.

Escribí primero la prueba que lo muestra: al llamar la función dos veces, el primer resultado incluía las ventas de la segunda. Pytest falló con `AssertionError: {'Ford': 1000.0, 'Toyota': 500.0} == {'Ford': 1000.0}`.

La solución fue usar `acumulado=None` y crear el diccionario dentro de la función con `if acumulado is None`. Así cada llamada recibe uno nuevo y la función hace lo que dice su docstring.

## Reflexión

Antes pensaba que los linters servían para regañar. Ahora los leo como pistas:

- `N802`: usar nombres en `snake_case`.
- `E711`: comparar con `is None`.
- `F841`: borrar código que no se usa.
- `E722`: evitar el `except` sin tipo de error.

Mi decisión favorita fue separar los cambios de estilo de los de lógica en commits distintos. Con más tiempo ampliaría las pruebas con casos límite: precio negativo, venta sin campos y fecha inválida. Y escribiría siempre la prueba antes de la corrección: ver el rojo de pytest fue lo que me hizo entender el bug.

## Ayudas externas

Usé un asistente de IA, opencode, como guía: me explicó conceptos de git, sugirió comandos y me ayudó a interpretar los errores de ruff y pytest. Escribí y ejecuté todos los comandos yo, revisando cada salida, y redacté este informe con base en mi experiencia. También consulté la documentación de ruff y de pytest. Declaro este uso según las reglas del curso.
EOF