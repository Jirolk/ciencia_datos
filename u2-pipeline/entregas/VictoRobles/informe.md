# Informe U2: Pipeline de pronóstico del clima con dlt y DuckDB

## Qué construí

Hice un pipeline que consulta la API pública de Open-Meteo y obtiene el pronóstico por hora, durante tres días, para Asunción (temperatura y precipitación). Con dlt se cargo esos datos en data.duckdb, en la tabla clima.pronostico_horario, que queda con 72 filas. Después, verificar_datos.py abre la base y, con SQL, cuenta las horas cargadas, busca la hora más calurosa y cuenta las horas con lluvia. Elegí esta API porque no pide clave y porque el clima es un dato conocido y logico para facilitar mi interpretación.

Algo que aprendí es que estos datos son pronósticos de un modelo, no mediciones. Además, la API ajusta el punto pedido a la celda más cercana de su cuadrícula: pedí latitud -25.26 y longitud -57.58, y devolvió -25.272408 y -57.600006.

## Decisiones de diseño

La API entrega los datos en listas paralelas: una lista de horas, una de temperaturas y una de precipitaciones, donde la posición 0 de cada una corresponde a la misma hora. Si le entregaba ese bloque tal cual a dlt, él habría separado cada lista en tablas hijas, difíciles de consultar. Por eso escribí la función filas_por_hora(), que une las listas con zip y arma una fila por hora, y se la entrego ya ordenada a dlt. Usé strict=True para que falle con un error claro si las listas tuvieran distinto largo, en vez de cortar datos en silencio.

Pedí timezone=auto para que las horas vengan en hora local de Paraguay (GMT-3) y no tener que convertirlas. También agregué la latitud y la longitud en cada fila, para saber de qué lugar es cada dato.

Usé write_disposition="replace": cada ejecución reemplaza la tabla, así que ejecutarlo dos veces no duplica filas. Separé pedir_pronostico() del resto para poder reemplazar la llamada a internet por una respuesta falsa en las pruebas.

## El esquema automático de dlt

 dlt inspeccionó los datos y creó la tabla sola. Con DESCRIBE clima.pronostico_horario vi que guardó time como TIMESTAMP WITH TIME ZONE, aunque la API la entrega como texto (por ejemplo "2026-10-23T00:00"); dlt reconoció que era una fecha y hora. temperature_2m, precipitation, latitude y longitude quedaron como DOUBLE. También agregó dos columnas propias, _dlt_load_id y _dlt_id, que identifican en qué carga llegó cada fila y le dan un identificador único.

 Me parece muy beneficioso que dlt hiciera esto automáticamente peor de igual manera es muy importante saber como trabaja para no incurrir en errores.

## Mi opinión sobre DuckDB

Con DuckDB toda la base sea un solo archivo, sin instalar ni configurar un servidor, y se consulta con SQL desde Python, lo cual es muy practico para bases de datos pequeñas, de prueba y como en estos casos de practicas.

## Problemas, mejoras y ayudas externas

AL ejecutar ruff format me marcó un detalle de formato en la última línea de mis archivos y lo corregí con ruff format.

Con más tiempo agregaria más variables como humedad o viento, otras ciudades de Paraguay y tambien las regiones occidental y oriental que varia fuertemente el clima en estas regiones.