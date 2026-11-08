# Informe de unidad

Informe técnico acotado para el cierre de cada unidad

---

## Unidad: U2 - Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Fabio Cesar Alfonso Nuñez (`fabioAlfonsoUNC`)

**Fecha:** 25/10/2026

**Tag de cierre:** `u2-completa`

### Que se hizo

Se construyó un pipeline de ingesta de datos reproducible en Python utilizando `dlt` y `DuckDB` para extraer, normalizar y almacenar información geográfica de las ciudades de Paraguay desde la API pública `countries.dev` (`https://countries.dev/cities?country=PY`).

El trabajo se desarrolló en tres etapas secuenciales:
1. **Extracción y carga (`pipeline.py`):** Se implementó el recurso `paraguay_cities_resource` decorado con `@dlt.resource` y empaquetado en la fuente `@dlt.source` (`paraguay_cities_source`). El script consume el endpoint mediante `requests`, valida el estado HTTP con `raise_for_status()` y persiste los datos localmente en el archivo `data.duckdb` bajo el esquema `raw_paraguay` y la tabla `ciudades_py`. Durante la carga, el esquema automático de `dlt` infirió los tipos de datos relacionales (`BIGINT`, `DOUBLE`, `VARCHAR`), convirtió las claves del JSON original de `camelCase` a `snake_case` (por ejemplo, `geonameId` pasó a `geoname_id` y `countryCode` a `country_code`) e inyectó columnas de auditoría (`_dlt_load_id` y `_dlt_id`).
2. **Verificación y consulta analítica (`verificar_datos.py`):** Se programó un script de validación que abre `data.duckdb` en modo de solo lectura (`read_only=True`). Trabajar con DuckDB resultó sumamente ágil al operar como un motor analítico OLAP embebido sin necesidad de levantar un servidor externo: al final del flujo, el script ejecuta consultas SQL que verifican el conteo total de registros, filtran el Top 5 de ciudades más pobladas de Paraguay (encabezado por Asunción con 1,482,200 habitantes) e inspeccionan las columnas normalizadas mediante `DESCRIBE`.
3. **Pruebas y calidad de código (`test_pipeline.py`):** Se implementaron tres pruebas unitarias con `pytest` y `unittest.mock.patch` (validación de estructura del recurso, respuesta vacía `[]` y fallo de conexión), verificando el cumplimiento de estilo y formato con `ruff check` y `ruff format --check`.

### Una decisión de diseño, explicada

Una decisión clave de diseño fue configurar el recurso con `write_disposition="replace"` en lugar de utilizar `append` o `merge`, además de declarar explícitamente el destino como `dlt.destinations.duckdb("data.duckdb")`.

Se eligió `replace` porque el endpoint de ciudades de Paraguay devuelve un catálogo estático completo en cada consulta y no una serie de eventos incrementales con marcas de tiempo. Si se hubiese dejado el comportamiento por defecto (`append`), cada ejecución de prueba de `pipeline.py` habría duplicado la totalidad de las ciudades dentro de la tabla `raw_paraguay.ciudades_py`, alterando los conteos en `verificar_datos.py`. Por otra parte, configurar una estrategia `merge` añadía complejidad innecesaria de deduplicación para un dataset maestro de tamaño acotado. Con `replace`, el pipeline garantiza idempotencia total y mantiene el esquema y la tabla limpios en cada corrida.

### Un problema que apareció

Al ejecutar por primera vez la suite de pruebas con `pytest`, falló el test `test_caso_borde_error_conexion` en `test_pipeline.py`. Inicialmente se había simulado un corte de red mediante `side_effect=requests.exceptions.ConnectionError`, esperando capturar esa misma excepción directamente con `pytest.raises(requests.exceptions.ConnectionError)` al consumir el generador `list(pipeline.paraguay_cities_resource())`.

Sin embargo, la prueba falló porque `dlt` no propaga la excepción cruda de `requests` hacia el exterior. Analizando el *traceback* de `pytest`, se descubrió que el iterador interno de `dlt` (`ManagedPipeIterator`) intercepta cualquier excepción lanzada dentro de un generador decorado con `@dlt.resource` y la encapsula dentro de su propia excepción `dlt.extract.exceptions.ResourceExtractionError`. Para resolverlo, se importó `ResourceExtractionError` en el archivo de pruebas, se ajustó el bloque a `pytest.raises(ResourceExtractionError)` y se añadió una validación sobre el atributo `exc_info.value.__cause__` para confirmar que la causa subyacente seguía siendo el `ConnectionError` simulado.

### Que harías distinto con mas tiempo

Con más tiempo, mejoraría dos aspectos de la implementación actual:
- **Carga incremental con `merge` y contratos de datos:** Si la fuente escalara a múltiples países o actualizaciones frecuentes, cambiaría la estrategia a `write_disposition="merge"` utilizando `primary_key="geoname_

**Declaración de herramientas:** Durante el desarrollo se consultó la documentación oficial de `dlt` y `DuckDB`, y se empleó el asistente de IA Gemini como apoyo para la configuración de pruebas con `unittest.mock`, la identificación de la excepción `ResourceExtractionError` y la estructuración de este informe. Todo el código fue revisado, ejecutado y comprendido en su totalidad.