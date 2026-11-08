# Informe de unidad 2 — mi primer pipeline con dlt y DuckDB

**Nombre:** Blas Antonio Zavala
**Fecha:** 31 de octubre de 2026
**Tag de cierre:** `u2-completa`

## Qué se hizo

Comencé sincronizando mi fork con el repositorio del curso, que tenía más de cien commits nuevos, ejecuté `uv sync` y creé la rama `u2/5835773-blas`. El pipeline (`pipeline.py`) descarga los cien posts de JSONPlaceholder con `requests`, con espera y validación de la respuesta, y los entrega a dlt mediante un recurso llamado `posts`, que carga en `data.duckdb` bajo el esquema `u2_posts`. El verificador, `verificar_datos.py`, abre la base en modo solo lectura, cuenta los registros —salieron cien— y filtra los cinco primeros posts del usuario uno. Las pruebas cubren la estructura del recurso y dos casos borde sin red.

## Una decisión de diseño, explicada

Elegí `write_disposition="merge"` con `primary_key="id"` en lugar de `append`: JSONPlaceholder devuelve siempre las mismas cien publicaciones y con `append` cada re-ejecución duplicaría la tabla, mientras que `merge` actualiza las filas existentes por su identificador. El recurso además acepta `filas` opcionales: si llegan datos, no consulta la API. Esa separación entre conseguir y procesar datos permitió probar la lógica con datos inventados y que los tests corran sin internet. También resolví la ruta de la base con `Path(__file__)` para que quede siempre junto al script.

## El esquema automático de dlt

dlt construye el esquema solo: al primer load infirió los tipos y creó la tabla `posts` dentro de `u2_posts`. Lo primero que noté es que renombra las claves a snake_case, así que `userId` llegó como `user_id`. Mi forma de lidiar con eso fue no dar nada por sentado: dejé que dlt infiriera, pero verifiqué el resultado con una consulta real en vez de confiar a ciegas; si la API cambiara su estructura, la validación de la respuesta y el conteo lo detectarían enseguida.

## DuckDB desde la práctica

Trabajar con DuckDB me pareció lo más cómodo del ejercicio: sin servidor que instalar ni levantar, la base es un solo archivo de unos dos megabytes y se consulta con SQL normal desde Python. Abrirla en modo lectura desde `verificar_datos.py` transmite confianza: una consulta no puede romper los datos. También me gustó que dlt y DuckDB se entienden sin configuración: el pipeline escribe y la consulta lo lee de inmediato. Como límite, eché de menos inspeccionar el esquema sin escribir SQL a mano.

## Un problema que apareció

`verificar_datos.py` no ejecutaba: Python decía que el archivo no existía, pero git lo tenía commiteado y `git status` no mostraba ningún borrado. La clave la dio `ls -la`: el nombre del archivo terminaba en un espacio, un carácter que git conserva sin protestar y que la terminal escribe sin mostrar. Lo corregí con `git mv` entre comillas y un commit dedicado. La lección: cuando un comando dice que algo no existe y tú ves que existe, revisa los nombres carácter a carácter antes de sospechar de git.

## Qué haría distinto con más tiempo

Escribiría primero las pruebas que el código, como sugiere el TDD: hice las pruebas después del pipeline y eso se nota en lo que decidí testear. Añadiría un paso que compare el conteo de origen y destino, y documentaría el esquema esperado de la API dentro del propio script para que cualquier cambio futuro se note en las pruebas.

## Ayudas externas

Usé un asistente de IA, opencode, como guía: me ayudó a estructurar el plan, a elegir `merge` frente a `append` y a interpretar los errores de ruff, pytest y git. Todos los comandos y todo el código pasaron por mis manos en el Codespace: los ejecuté, verifiqué cada salida y me consta qué hace cada línea. Consulté además la documentación de dlt sobre recursos y write dispositions, y la de DuckDB para las consultas. Declaro este uso conforme a las reglas del curso.