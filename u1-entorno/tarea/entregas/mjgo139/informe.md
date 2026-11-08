# Informe U1: mi primer aporte reproducible

**Nombre:** Marcelo Javier González Olmedo

**Usuario de GitHub:** mjgo139

**Fecha:** 16/10/2026

## Entorno

Trabajé dentro de un GitHub Codespace abierto desde mi fork de `ciencia_datos`. El Codespace usa el Dev Container del curso: una imagen de Python 3.12 con `uv`, que al crearse ejecuta `uv sync --all-groups` e instala las dependencias en la carpeta `.venv`. Así el entorno es igual para todos y no depende de mi computadora.

Al ejecutar el verificador por primera vez, no terminó con OK:

```
pre-commit: NO ENCONTRADO
FALTA:
  - instalar pre-commit (pip install -r requirements.txt)
```

El mensaje mencionaba un `requirements.txt` que no existe. `pre-commit` figura en `uv.lock` pero no en `pyproject.toml`, por eso `uv sync` no lo instalaba. Lo instalé en el entorno virtual con la misma versión que fija el lock:

```
uv pip install pre-commit==4.6.2
python u1-entorno/tarea/verificar_entorno.py
...
OK
```

No usé `uv add`, porque eso modifica `pyproject.toml` y `uv.lock`, y el pull request debía tocar solo mi carpeta.

## Flujo de Git

Hice un fork del repositorio del curso y creé la rama `u1/mjgo139` antes de modificar cualquier archivo. Dividí el trabajo en cinco commits pequeños, uno por cada decisión:

1. Copia original de `ejercicio.py`, para que quede registrado el estado inicial.
2. Correcciones automáticas de `ruff check --fix` y `ruff format`.
3. Correcciones a mano de lo que ruff no podía resolver solo.
4. Pruebas con pytest.
5. Este informe.

Separar lo automático de lo manual muestra qué cambió la herramienta y qué decidí yo. En cada commit agregué los archivos por su nombre, sin `git add .`, porque `uv` modifica `uv.lock` por su cuenta y no quería subir ese cambio.

`ruff check` encontró 10 errores. Cuatro se corrigieron solos (tres imports sin usar y una f-string sin variables) y `ruff format` resolvió el `if` en una sola línea. A mano corregí cinco: el nombre `ParseFecha` pasó a `parse_fecha`, la comparación `== None` pasó a `is None`, borré la variable `total` que no se usaba, cambié el `except` genérico por las excepciones concretas y corregí el valor por defecto de `resumen_por_marca`.

## Un problema que apareció

Tuve dos problemas. El primero fue simple: después de reabrir la terminal, `ruff check ejercicio.py` respondía `E902 No such file or directory`. La terminal había vuelto a la raíz del repositorio. Lo resolví volviendo a mi carpeta con `cd`.

El segundo era el error real del ejercicio, la advertencia B006 de ruff. La función `resumen_por_marca` tenía `acumulado={}` como valor por defecto. Python crea ese diccionario una sola vez, al definir la función, así que todas las llamadas comparten el mismo objeto y van sumando las ventas anteriores. Lo cambié por `acumulado=None` y creo el diccionario dentro de la función.

Escribí una prueba que llama dos veces a la función con marcas distintas. Con el código original falla, y la variable de la primera llamada termina conteniendo también la marca de la segunda:

```
AssertionError: assert {'Chevrolet': 22000.0, 'Mazda': 9500.0} == {'Chevrolet': 22000.0}
```

Con la corrección pasan las cuatro pruebas. El otro caso borde es una fecha del 29 de febrero de un año bisiesto.

```
4 passed in 0.02s
```

## Reflexión

Lo más importante que me llevo es que el estilo y el comportamiento no son lo mismo. Ruff marcó el diccionario mutable como una advertencia más, pero solo la prueba demostró que producía resultados incorrectos. También entendí que un entorno reproducible no es solo “que funcione en mi máquina”: el repositorio tenía una diferencia entre `pyproject.toml` y `uv.lock`, y cualquiera que lo abriera desde cero se encontraba con el mismo error.

Con más tiempo, escribiría más pruebas para `descripcion_venta` y `separar_nombre_id`, que tienen más casos posibles de los que cubrí.

## Ayudas externas

Usé Claude (IA) como apoyo para entender los errores y ordenar el informe. Ejecuté todos los comandos y puedo explicar cada línea entregada.