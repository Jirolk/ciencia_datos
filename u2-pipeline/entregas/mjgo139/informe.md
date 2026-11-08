# Informe U2: Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Marcelo Javier González Olmedo

**Usuario de GitHub:** mjgo139

**Fecha:** 25/10/2026

## Qué hice

Construí un pipeline que extrae datos de la API pública JSONPlaceholder y los guarda en una base DuckDB local llamada `data.duckdb`, dentro del esquema `jsonplaceholder`. Cargo dos tablas: `usuarios` (10 registros, endpoint `/users`) y `tareas` (200 registros, endpoint `/todos`). Después, `verificar_datos.py` consulta con SQL cuántas tareas completó cada usuario.

Trabajé en la rama `u2/mjgo139`, creada desde `main` para no arrastrar nada de la U1.

## Decisiones de diseño

**Elegí JSONPlaceholder.**. JSONPlaceholder entrega cada endpoint en una sola respuesta.

**Dos recursos y una fuente.** Cada endpoint es un `@dlt.resource` y los dos se agrupan en un `@dlt.source`. Se cargan juntos, y tener dos tablas me permitió usar un `JOIN`.

**`write_disposition="replace"` con `primary_key="id"`.** La API siempre devuelve el conjunto completo, así que reemplazo la tabla en cada ejecución. Con `append`, correr el pipeline dos veces duplicaría las filas.

**`raise_for_status()` y `timeout=30`.** Si la API falla o no responde, el pipeline se detiene en lugar de cargar datos incompletos.

**Ruta fija junto al script.** `data.duckdb` se crea en mi carpeta, y un `.gitignore` evita subirlo, como piden las reglas del curso.

## Cómo lidié con el esquema automático de dlt

En lugar de limpiar cada registro a mano, dejé que dlt construyera el esquema y revisé qué hacía. Encontré tres transformaciones:

- **Aplanó los datos anidados.** Cada usuario trae `address`, que contiene a su vez `geo`, y también `company`. dlt los convirtió en columnas planas unidas con doble guion bajo: `address__city`, `address__geo__lat` y `company__name`.
- **Normalizó los nombres a snake_case.** `userId` pasó a `user_id` y `catchPhrase` a `company__catch_phrase`. Por eso el `JOIN` usa `t.user_id`.
- **Infirió los tipos.** `id` y `user_id` quedaron como `BIGINT`, los textos como `VARCHAR` y `completed` como `BOOLEAN`. Por eso puedo filtrar con `WHERE NOT completed` sin conversiones.

Además, dlt agregó las columnas `_dlt_id` y `_dlt_load_id` a cada fila y sus tablas de control (`_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`).

## Evidencias de ejecución

Ejecuté todo dentro de mi Codespace. `python pipeline.py` terminó con el mensaje `LOADED and contains no failed jobs` y creó `data.duckdb` en mi carpeta. Después, la verificación mostró los datos cargados:

```
$ python verificar_datos.py
Usuarios: 10
Tareas: 200
Tareas pendientes: 110

Avance por usuario (completadas / total):
  Chelsey Dietrich (Roscoeview): 12/20
  Clementina DuBuque (Lebsackbury): 12/20
  Leanne Graham (Gwenborough): 11/20
  Nicholas Runolfsdottir V (Aliyaview): 11/20
  Kurtis Weissnat (Howemouth): 9/20
  Ervin Howell (Wisokyburgh): 8/20
  Glenna Reichert (Bartholomebury): 8/20
  Clementine Bauch (McKenziehaven): 7/20
  Mrs. Dennis Schulist (South Christy): 6/20
  Patricia Lebsack (South Elvis): 6/20
```

Cada usuario tiene 20 tareas; Chelsey Dietrich y Clementina DuBuque completaron más, con 12.

```
$ pytest -v
collected 4 items

test_pipeline.py::test_recursos_entregan_los_registros_de_la_api PASSED      [ 25%]
test_pipeline.py::test_carga_en_duckdb_con_esquema_aplanado PASSED           [ 50%]
test_pipeline.py::test_respuesta_vacia_no_crea_registros PASSED              [ 75%]
test_pipeline.py::test_error_de_conexion_detiene_la_extraccion PASSED        [100%]

4 passed in 2.16s
```

Las pruebas no usan la red: reemplazan `requests.get` por una API simulada. Comprueban que los recursos entregan los registros, que dlt guarda las tablas con las columnas aplanadas y dos casos borde: una respuesta vacía y un error de conexión.

## Qué me pareció trabajar con DuckDB

Me resultó muy práctico. Es un solo archivo, sin servidor, y desde Python se consulta con SQL normal en dos líneas. Abrí la base en modo `read_only` en la verificación para no modificarla por error. Una limitación es que solo un proceso puede escribir a la vez, así que no conviene tener la base abierta en otra herramienta mientras corre el pipeline.

## Reflexión

Lo más valioso fue ver que dlt no solo copia datos: decide nombres, tipos y estructura. Si no hubiera revisado el esquema, mi consulta habría fallado buscando `userId`. También aprendí a correr `ruff format --check` antes de entregar: al pegar el código, los tres archivos quedaron sin el salto de línea final, y lo corregí con `ruff format` en un commit aparte. Con más tiempo, cargaría también las publicaciones y los comentarios, y probaría `write_disposition="merge"` para actualizar solo los registros que cambian.

## Ayudas externas

Usé Claude (IA) como apoyo para ordenar el informe. Ejecuté todos los comandos y puedo explicar cada línea entregada.