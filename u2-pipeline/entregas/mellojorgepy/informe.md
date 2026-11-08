# Informe de unidad

## Unidad: U2 — Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Jorge Daniel Mello-Román

**Fecha:** 30 de octubre de 2026

**Rama:** `u2/mellojorgepy`

### Qué se hizo

Construí un pipeline que extrae todos los personajes de la Rick and Morty API, los valida, los aplana y los carga en `data.duckdb`, en el esquema `rick_and_morty` y la tabla `personajes`. El trabajo quedó en tres scripts:

- `pipeline.py`: define el recurso `personajes` con `@dlt.resource`, recorre la paginación siguiendo `info.next` y ejecuta `pipeline.run()` contra DuckDB.
- `verificar_datos.py`: abre la base en modo solo lectura y ejecuta tres consultas SQL: el conteo total, la distribución por estado y los humanos vivos con más episodios.
- `test_pipeline.py`: seis pruebas con pytest que no dependen de la red, porque las respuestas de la API se simulan con `monkeypatch`.

Al final corren sin errores `ruff check`, `ruff format --check`, el pipeline, la verificación y `pytest`.

**Evidencia de ejecución** (salida de `verificar_datos.py`):

```text
Registros en rick_and_morty.personajes: 826

== Personajes por estado
estado | n
Alive | 439
Dead | 287
unknown | 100

== Top 5 especies
especie | n
Human | 366
Alien | 205
Humanoid | 68
Animal | 55
Robot | 51

== Humanos vivos con más episodios
id | nombre | n_episodios
1 | Rick Sanchez | 51
2 | Morty Smith | 51
3 | Summer Smith | 42
4 | Beth Smith | 42
5 | Jerry Smith | 39
```

### Decisiones de diseño

**Aplanar antes de cargar.** Cada personaje trae objetos anidados (`origin`, `location`) y una lista de URLs (`episode`). El esquema automático de dlt convierte los objetos en columnas con doble guion bajo (`origin__name`, `origin__url`) y las listas en una tabla hija (`personajes__episode`) unida por `_dlt_parent_id`. Funciona, pero deja tres tablas y nombres poco legibles para una consulta básica. Como la tarea pedía una tabla limpia, la función `limpiar_personaje` conserva solo el nombre del origen y de la ubicación y reduce la lista de episodios a un conteo (`n_episodios`). Pierdo el detalle de qué episodios son, pero gano una tabla única y fácil de consultar. Si después hiciera falta ese detalle, lo cargaría como un segundo recurso.

**`replace` y no `append`.** La API devuelve siempre el catálogo completo, así que cada ejecución reemplaza la tabla. Con `append`, correr el pipeline dos veces duplicaría los registros. Igual declaré `primary_key="id"` para documentar la clave.

**Validar temprano.** Si un registro llega sin `id`, `name`, `status`, `species` o `gender`, el pipeline lanza `ValueError` en vez de cargar una fila incompleta. Prefiero que la ejecución falle con un mensaje claro a descubrir el problema más tarde en una consulta.

**Casos borde de la API.** La API responde 404 cuando un filtro no tiene resultados. `descargar_pagina` trata ese caso como una página vacía, mientras que un error de conexión se propaga y detiene el pipeline. Uso el cliente `requests` de dlt, que reintenta automáticamente ante fallos transitorios.

### Un problema que apareció

En una carga de prueba dlt mostró este aviso: la columna `tipo` *did not receive any data… could not have their types inferred*. Muchos personajes tienen `type` vacío, que convertí a `NULL`. Si un lote no trae ningún valor, dlt no puede inferir el tipo y no crea la columna, de modo que el esquema dependería de los datos de cada ejecución. Lo resolví declarando el esquema completo en `columns=` del recurso. Ahora las diez columnas existen siempre con su tipo (`creado` como `TIMESTAMP`, `n_episodios` como `BIGINT`). Esto me mostró el límite del esquema automático: es cómodo para explorar, pero en un pipeline reproducible conviene fijar los tipos.

### Sobre DuckDB

DuckDB fue lo más sencillo de la unidad: no requiere servidor, la base es un único archivo y desde Python basta `duckdb.connect()`. Las columnas de control de dlt (`_dlt_load_id`, `_dlt_id`) permiten rastrear de qué carga viene cada fila. Una precaución: DuckDB admite una sola conexión de escritura, por lo que la verificación abre la base con `read_only=True`. También agregué un `.gitignore` en mi carpeta para no subir `data.duckdb`, que se regenera ejecutando el pipeline.

### Qué haría distinto con más tiempo

Las pruebas simulan la API, de modo que no detectarían un cambio real en su formato. Agregaría una prueba de integración opcional contra la API real y una verificación de conservación de filas, como en el laboratorio, que compare `info.count` con las filas cargadas.

### Uso de IA

Usé Claude (Anthropic) como apoyo para estructurar el código, las pruebas y la redacción. Revisé, ejecuté y puedo explicar cada línea entregada.
