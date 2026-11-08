# Informe de unidad

## Unidad: 1 · Entorno de trabajo y reproducibilidad

**Nombre:** Jorge Daniel Mello Román (`mellojorgepy`)

**Fecha:** 21/10/2026

**Tag de cierre:** `u1-completa`

### Qué se hizo

Hice un fork del repositorio del curso, lo abrí en un Codespace y verifiqué el entorno.
Después copié `ejercicio.py` a mi carpeta de entrega, corregí el estilo con `ruff` (primero
lo automático, luego lo manual), escribí nueve pruebas con `pytest` y corregí el error real
que esas pruebas encontraron. Al final, `ruff check`, `ruff format --check` y `pytest`
quedan en verde dentro de mi carpeta.

### Entorno

El contenedor se construye desde `.devcontainer/` (Python 3.12 y `uv`) y, al crearse, ejecuta
`uv sync --all-groups`. La primera vez, `verificar_entorno.py` terminó con
`pre-commit: NO ENCONTRADO`. La causa es que `uv.lock` ya incluye `pre-commit>=4.6.2` en el
grupo `dev`, pero `pyproject.toml` no lo declara, así que `uv sync` vuelve a resolver sin él.
Lo fijé con `uv add --dev "pre-commit>=4.6.2"`, que declara la dependencia en `pyproject.toml`
y deja el lock coherente (`uv lock --check` pasa). Con eso la verificación terminó en `OK`:

```
Entorno: GitHub Codespaces
Python: 3.12.11
pytest: 9.1.1
ruff: 0.16.10
pre-commit: 4.7.0
git: git version 2.50.1

OK
```

Este cambio no va en el PR, porque la entrega solo puede tocar mi carpeta. Lo dejo
señalado en la descripción del PR para que se corrija en el repositorio del curso.

### Flujo de Git

Trabajé en la rama `u1/mellojorgepy` con seis commits pequeños, cada uno con un solo
propósito: (1) copiar el original sin cambios, como línea base; (2) aplicar lo que `ruff`
corrige solo; (3) las correcciones manuales de estilo; (4) agregar las pruebas, dos de las
cuales fallaban a propósito; (5) corregir el error que esas pruebas mostraban; (6) agregar este informe. Separar lo
automático de lo manual permite al revisor ver en el diff qué decidí yo y qué hizo la
herramienta. El PR va al repositorio del curso y solo toca
`u1-entorno/tarea/entregas/mellojorgepy/`.

### Una decisión de diseño, explicada

En `descripcion_venta` el original tenía un `except:` sin tipo. Podía cambiarlo por
`except Exception`, que calla a `ruff`, pero preferí `except (KeyError, TypeError, ValueError)`.
Son exactamente los fallos esperables al leer el precio: que falte la clave, que el valor
sea `None` o que sea un texto no numérico. Así conservo el comportamiento descrito (precio
inválido se reporta como 0) sin esconder errores de programación ni interrupciones del
usuario. También renombré `ParseFecha` a `parse_fecha`, porque PEP 8 pide minúsculas con
guion bajo para funciones.

### Un problema que apareció

`ruff` marcaba B006 en `resumen_por_marca(ventas, acumulado={})` y no lo corregía solo.
Parecía una advertencia de estilo, pero era el error real del ejercicio. Python crea ese
diccionario una única vez, al definir la función, y todas las llamadas comparten el mismo.
Lo comprobé escribiendo primero las pruebas: `resumen_por_marca([])` devolvía las sumas de
llamadas anteriores en lugar de `{}`, y dos pruebas fallaron:

```
FAILED test_ejercicio.py::test_resumen_por_marca_no_arrastra_llamadas_anteriores
FAILED test_ejercicio.py::test_resumen_por_marca_lista_vacia
2 failed, 7 passed
```

Lo resolví usando `None` como valor por defecto y creando un diccionario nuevo dentro de
la función. Después, las nueve pruebas pasaron.

### Reflexión: qué haría distinto con más tiempo

Aprendí que una advertencia del linter puede esconder un error de lógica, y que una prueba
bien elegida lo convierte en algo visible y verificable. Con más tiempo, activaría los hooks
de `pre-commit` del repositorio para que `ruff` se ejecute antes de cada commit, en lugar de
recordarlo a mano. También agregaría anotaciones de tipo a las funciones y pruebas
parametrizadas con más fechas y formatos de nombre. Como limitación, `separar_nombre_id`
no distingue un nombre que termina en número por error de uno con identificador real.

### Ayudas externas

Usé Claude (Anthropic) como asistente de IA para revisar el repositorio, diagnosticar por
qué faltaba `pre-commit`, proponer las correcciones y las pruebas y redactar un borrador de
este informe. Ejecuté y revisé cada paso en el Codespace, y puedo explicar cada línea
entregada. Consulté además la documentación de `ruff` (reglas B006, E711, E722 y N802) y
de `uv`.
