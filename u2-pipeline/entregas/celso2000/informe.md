# Informe de unidad

**Unidad:** U2 · Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Celso Damián Ibáñez Meza

**Fecha:** 25 de octubre de 2026

**Tag de cierre:** `u2-completa`

## Qué se hizo

Se construyó un pipeline de datos que extrae la lista de usuarios de la API pública JSONPlaceholder y la almacena en una base DuckDB local. En primer lugar, se definió un recurso de dlt (`users`) que solicita los datos y verifica la respuesta; luego, se configuró la carga hacia `data.duckdb`, dentro del esquema `jsonplaceholder`. Posteriormente, se escribieron `verificar_datos.py`, que consulta la base mediante SQL, y `test_pipeline.py`, con tres pruebas de pytest que simulan la API. Al finalizar, se obtuvieron 10 usuarios cargados y las tres pruebas se ejecutaron sin errores.

## Una decisión de diseño, explicada

**Decisión 1: `replace` en lugar de `append`.** Se configuró el recurso con `write_disposition="replace"`. Con `append`, correr el pipeline dos veces habría dejado 20 filas con los mismos 10 usuarios duplicados; con `replace`, cada ejecución reemplaza la tabla completa y el resultado es el mismo sin importar cuántas veces se corra (idempotencia). Como JSONPlaceholder devuelve siempre los mismos 10 usuarios, esta opción resultó la más adecuada. El modo `merge` también era posible, pero innecesario para 10 registros estáticos. Tras varias ejecuciones, la tabla conservó 10 filas.

**Decisión 2: esquema automático de dlt.** No se definió un esquema explícito: se dejó que dlt lo infiera automáticamente y se verificó el resultado con `describe` en DuckDB. dlt normalizó los nombres (`company.catchPhrase` pasó a `company__catch_phrase`), aplanó los objetos anidados (`address__geo__lat`), agregó las columnas `_dlt_id` y `_dlt_load_id` y creó tres tablas de control (`_dlt_loads`, `_dlt_version` y `_dlt_pipeline_state`). Los tipos se infirieron de los datos: `id` quedó como BIGINT y el resto como VARCHAR, incluidas las coordenadas, que la API entrega como texto. La ventaja fue no escribir ningún `CREATE TABLE`; el riesgo, que un cambio en la API modifique la tabla sin aviso.

## Un problema que apareció

Durante la verificación de datos, la segunda consulta de `verificar_datos.py` falló con el error `Parser Error: syntax error at or near "."`. DuckDB mostró la consulta recibida (`LINE 1`) y en ella se observó que `address__city` y `from` habían quedado unidos como `address__cityfrom`, porque se había perdido el espacio entre dos fragmentos de texto concatenados. Se resolvió reescribiendo la consulta con triple comilla, una cláusula por línea, lo que eliminó la dependencia de espacios al final de cada fragmento. Como aprendizaje, el mensaje de error de DuckDB mostró la consulta exacta recibida, lo que facilitó ubicar la falla.


## Qué haría distinto con más tiempo

Se identificaron dos limitaciones. Primero, `data.duckdb` se crea en el directorio desde donde se ejecuta el script, por lo que depende de correrlo desde la raíz del repositorio; sería más robusto definir la ruta respecto del propio archivo. Segundo, las coordenadas quedaron como texto; con más tiempo se definirían los tipos de forma explícita y se agregaría una prueba con una base temporal.

## Impresiones sobre DuckDB

Este fue el primer contacto con DuckDB y se destacó por su cercanía con el código: al no requerir un servidor, la base se redujo a un único archivo (`data.duckdb`), consultable con SQL estándar desde Python y sin configuración previa, lo que facilitó inspeccionar lo que dlt había creado, por ejemplo con `describe`. Como contrapartida, su modelo de un único proceso escritor a la vez exige cuidado al abrir la base desde otras herramientas, por lo que la verificación se realizó en modo de solo lectura.

## Evidencias de ejecución

```
$ uv run python u2-pipeline/entregas/celso2000/pipeline.py
Load package 1792968457.8581371 is LOADED and contains no failed jobs

$ uv run python u2-pipeline/entregas/celso2000/verificar_datos.py
Usuarios cargados: 10

$ uv run pytest u2-pipeline/entregas/celso2000
3 passed in 0.86s

```

## Uso de IA

Se utilizó Claude (Anthropic) como asistente durante la unidad: explicó los conceptos paso a paso, propuso la estructura inicial del código y de las pruebas, y colaboró en una primera redacción de este informe. El código se ejecutó, se probó y se corrigió en el entorno propio, y cada parte fue revisada para poder explicarla.