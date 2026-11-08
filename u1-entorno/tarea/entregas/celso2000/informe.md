# Informe de unidad

## Unidad: 1 - Entorno reproducible

**Nombre:** Celso Ibáñez

**Fecha:** 16/10/2026

**Tag de cierre:** u1-completa

### Entorno

Trabajé en un Codespace de GitHub creado desde mi fork del repositorio del curso. Ese Codespace levanta un Dev Container definido en `.devcontainer`, así que el entorno es el mismo para cualquiera. Dentro activé el entorno virtual `.venv`, una caja de Python aislada con las librerías del curso, y ejecuté `verificar_entorno.py`. Al principio faltaba `pre-commit`; después de instalarlo el script mostró Python 3.12.11, pytest, ruff, pre-commit y git, y terminó con OK.

### Flujo de Git

Hice un fork del repositorio `ubuntumb/ciencia_datos`, una copia en mi cuenta donde puedo escribir sin tocar el original, y creé la rama `u1/celso2000`. Trabajé con commits chicos, cada uno con un mensaje que explica el porqué: el ejercicio original, los arreglos automáticos de ruff, el formato, los arreglos manuales, la corrección del bug, las pruebas y el informe. Corrí ruff y pytest antes de commitear. Al final subí la rama a mi fork y abrí el pull request hacia el repositorio del curso.

### Una decisión de diseño, explicada

Cambié `acumulado={}` por `acumulado=None` en `resumen_por_marca` y creo el diccionario dentro de la función. Python crea el valor por defecto una sola vez, al definir la función, y lo reutiliza en cada llamada que no recibe un diccionario propio; con `{}`, las ventas de una llamada se sumaban a las de la siguiente. Con `None` cada llamada empieza limpia, y si alguien pasa su propio diccionario la función lo sigue usando. Prefería arreglarlo a mano antes que con `--unsafe-fixes`, para entender el cambio.

### Un problema que apareció

`verificar_entorno.py` dijo que faltaba `pre-commit` y sugería `pip install -r requirements.txt`, pero ese archivo no existe. Instalé con `pip install pre-commit` y el script seguía sin encontrarlo. Con `which python pip` vi la causa: `python` apuntaba a `.venv/bin/python`, pero `pip` a `/usr/local/bin/pip`, es decir, fuera del entorno virtual. Lo resolví con `uv pip install pre-commit`, que instala en el entorno activo, y apareció el OK. También `uv.lock` apareció modificado sin que lo tocara; lo restauré con `git restore` para que el PR cambie solo mi carpeta.

```
$ which python pip
/workspaces/ciencia_datos/.venv/bin/python
/usr/local/bin/pip
```

Además, el ejercicio escondía un bug real (`B006`): mi prueba falló con la versión original (`1 failed`) y pasó con la corregida (`3 passed`).

### Reflexión

Aprendí que un entorno es reproducible cuando está declarado en archivos y no depende de lo que yo instale a mano: `pre-commit` quedó instalado solo en mi Codespace, y con más tiempo le sugeriría al profe sumarlo a las dependencias del proyecto. También vi que ruff y pytest no son un trámite: una advertencia de estilo escondía un bug real y solo una prueba lo hizo visible. En Git me equivoqué una vez al hacer el commit antes de formatear y tuve que agregar otro; ahora corro formato, chequeo y pruebas antes de cada commit.

### Ayudas externas

Usé Claude, un asistente de IA, como guía paso a paso: me explicó los comandos de Git, ruff y pytest, me ayudó a diagnosticar el problema de `pre-commit`, me propuso el código de las correcciones y de las pruebas y me ayudó a redactar un borrador de este informe. Yo apliqué los cambios en mi Codespace, ejecuté las pruebas y revisé el informe. Además consulté el README de la tarea y vi en el chat del curso que a otros compañeros también les faltaba `pre-commit`. Puedo explicar cada línea de mi entrega.