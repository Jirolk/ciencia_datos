## Unidad: 2 — Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Lourdes Antonella Molinas

**Fecha:** 26 de octubre de 2026

**Tag de cierre:** `u2-completa`

### Qué se hizo

Construí un pipeline que descarga las cotizaciones oficiales del Banco Central del Paraguay (BCP)
desde la API pública Frankfurter, que no requiere clave: el valor de 1 dólar en guaraníes, reales,
pesos argentinos y euros desde el 1 de enero de 2026. Los datos quedan en `data.duckdb`, esquema
`tipo_cambio`, tabla `cotizaciones`.

Elegí esta fuente porque trabajo en el ambito financiero. Hoy armo mis indicadores en un Excel conectado a la
página del banco para extraer las cotizaciones del día, y quería ver cómo se haría con un pipeline
reproducible.

`verificar_datos.py` muestra el total cargado, el mínimo, máximo y promedio por moneda y el dólar
de los últimos 5 días. `test_pipeline.py` tiene cuatro pruebas que no usan internet: estructura de
la tabla, carga incremental, respuesta vacía y error de conexión.

### Una decisión de diseño, explicada

Usé **carga incremental con `merge`** en lugar de `replace` o `append`. Las cotizaciones se
publican una vez por día y las anteriores no cambian, así que no tiene sentido descargar todo el
año en cada ejecución. Con `dlt.sources.incremental("date")`, dlt guarda la última fecha cargada y
la siguiente corrida pide solo desde ahí.

Elegí `merge` con clave `(date, quote)` porque la API vuelve a enviar el último día ya cargado: con
`append` quedaría duplicado. Lo comprobé ejecutando el pipeline dos veces: la primera pidió desde
2026-01-01 y recibió 792 registros; la segunda pidió desde 2026-10-19, recibió 4 y el total no
cambió.

### Cómo lidié con el esquema automático de dlt

dlt creó la tabla y los tipos a partir del JSON. `rate` quedó bien como `DOUBLE`, pero `date` quedó
como `VARCHAR` porque la API envía la fecha como texto. Lo corregí con
`columns={"date": {"data_type": "date"}}`, y una prueba verifica que quede como `DATE`. También vi
que dlt agrega columnas propias (`_dlt_id`, `_dlt_load_id`) y la tabla `_dlt_pipeline_state`, donde
guarda la última fecha cargada.

### Un problema que apareció

El pipeline terminaba sin errores, pero la API devolvía 792 registros y la base tenía 788. Primero
supuse que había fechas repetidas; lo comprobé y no había ninguna. Después revisé las fechas más
antiguas de la respuesta: como el 1 de enero es feriado, la API incluyó el último día hábil
anterior, el 30 de diciembre de 2025. dlt descartó esas 4 filas porque son anteriores al valor
inicial del cursor. El filtro hizo lo correcto, pero aprendí a contrastar los totales y no confiar
solo en que el proceso "no dio error".

### Qué me pareció DuckDB

Muy práctico.
Comparado con mi Excel, el historial queda guardado y calculo mínimos o promedios con una consulta
en vez de mantener fórmulas a mano. Le veo futuro para automatizar mis reportes diarios.

### Qué haría distinto con más tiempo

La fecha inicial está fija en el código; sería mejor configurarla. Y el pipeline hoy se ejecuta a
mano: el siguiente paso sería programarlo para que corra solo cada día hábil.


