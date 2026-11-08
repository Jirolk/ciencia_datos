# Informe de unidad -- plantilla

Informe técnico acotado para el cierre de cada unidad

---

## Unidad: U1: Mi primer aporte reproducible

**Nombre:** David Helmut Reese Molinas

**Usuario GitHub:** 3241844facet

**Fecha:** 18 de Octubre de 2026

**Tag de cierre:** `u1-completa`

---

### Qué se hizo

En esta primera unidad configuré un entorno de desarrollo reproducible, corregí errores de estilo y bugs lógicos en
código legacy de Python, redacté un conjunto de pruebas automatizadas con Pytest y gestioné el flujo completo de
contribución mediante Git y GitHub.

#### Entorno
Realicé un fork del repositorio `curso-datos` y creé un entorno en GitHub Codespaces (Dev Container). Activé el
entorno virtual preconfigurado e introduje la verificación ejecutando `python u1-entorno/tarea/verificar_entorno.py`,
obteniendo la confirmación `OK`.

#### Flujo de Git
Creé la rama de trabajo `u1/3241844facet` y preparé la carpeta `u1-entorno/tarea/entregas/3241844facet/` con
`ejercicio.py`. Corregí los errores de estilo y bugs con `ruff check --fix` y `ruff format`. Luego desarrollé las
pruebas en `test_ejercicio.py`. Realicé tres commits pequeños explicativos siguiendo buenas prácticas de Git y
abrí el Pull Request desde mi rama hacia el repositorio original.

---

### Una decisión de diseño, explicada

Elegí estructurar la prueba de caso borde en `test_ejercicio.py` para evaluar de manera explícita la mutabilidad
acumulativa en la función `resumen_por_marca`, en lugar de solo probar un caso de uso estático aislado.

La función original definía `def resumen_por_marca(ventas, acumulado={}):`. En Python, las estructuras mutables
pasadas como argumento por defecto se evalúan una sola vez al definir la función. Si se llama a la función en
múltiples ocasiones consecutivas omitiendo el argumento `acumulado`, el estado del diccionario se conserva entre
invocaciones, provocando contaminación cruzada de datos (data leakage).

Diseñé la prueba `test_resumen_por_marca_llamadas_sucesivas_no_contaminar_acumulado`. Esta prueba invoca la función
dos veces consecutivas con conjuntos de ventas totalmente distintos. Al asertar que el resultado de la segunda
llamada no contiene las marcas de la primera, obligué a que la suite de pruebas fallara activamente con el código
defectuoso. Esto garantizó que la posterior refactorización a `acumulado=None` fuera verificable e indispensable.

---

### Un problema que apareció

Durante el proceso, `ruff check --fix` corrigió automáticamente errores de estilo, pero `pytest` ejecutaba con éxito
sin detectar anomalías en `descripcion_venta`.

Al revisar la advertencia `B001` de Ruff (`Do not use bare except`), noté que `descripcion_venta` capturaba cualquier
excepción genérica con un `except:` absoluto. Esto enmascaraba fallos graves, tales como la ausencia de claves
obligatorias (`KeyError`) o interrupciones de teclado (`KeyboardInterrupt`), transformando erróneamente cualquier
excepción en un precio con valor cero (`$0`).

Lo resolví refactorizando manualmente el bloque para capturar únicamente `ValueError`, la excepción esperada al
convertir cadenas no numéricas mediante `float()`. Agregué un caso de prueba en `test_ejercicio.py` especificando
`"sale_price": "No disponible"` para asegurar que el bloque manejara correctamente el error de conversión sin
silenciar otros fallos.

---

### Reflexión y ayudas externas

#### Reflexión
El proceso me permitió comprender la importancia del formateo automático, el lintering y la detección temprana de
bugs causados por mutabilidad en Python. Configurar pruebas rigurosas es clave para evitar regressiones en código
en producción.

#### Ayudas externas
Para completar la tarea utilicé la documentación oficial de Ruff sobre la regla `B006` (argumentos mutables por
defecto) https://docs-astral-sh.translate.goog/ruff/rules/mutable-argument-default/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc 
y la guía oficial de Pytest para estructurar las aserciones de los casos borde https://docs.pytest.org/en/stable/.

Asimismo, utilicé la asistencia de Gemini como apoyo interactivo para revisar la sintonía fina del conteo de palabras,
aclarar conceptos y validar la correcta alineación del contenido con la matriz de evaluaciones.

---

### Qué harías distinto con más tiempo

Con más tiempo, implementaría la validación de esquemas. Actualmente, las funciones asumen que los diccionarios contienen obligatoriamente las claves
`'car_make'`, `'car_model'` y `'sale_price'`. Si una estructura llega incompleta, el código lanza un `KeyError`.
Validar la entrada garantizaría un código más robusto ante datos corruptos.