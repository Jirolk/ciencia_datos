# Informe de unidad: U2, primer pipeline con dlt y DuckDB

**Nombre:** Sandro Roberto Castillo Delgado

**Usuario:** jirolk

**Fecha:** 2026-10-26

**Tag de cierre:** `u2-completa`

## Unidad: U2, primer pipeline con dlt y DuckDB

### Que se hizo

Preparé la implementación sobre la rama `u2/jirolk` y partí del repositorio fork ya configurado. El proyecto declara `dlt[duckdb]`, `duckdb`, `pytest` y `ruff` en `pyproject.toml`. Sincronicé las dependencias necesarias dentro del entorno virtual y comprobé las versiones disponibles.

La entrega extrae publicaciones de JSONPlaceholder, una API pública que no requiere autenticación ni claves. El archivo `pipeline.py` descarga el JSON, valida que la respuesta sea una lista y usa un recurso de dlt con nombre `posts` y disposición `replace`. El pipeline usa el nombre `jsonplaceholder_posts`, el esquema `u2_posts` y una base DuckDB llamada `data.duckdb`, ubicada dentro de la carpeta de entrega.

El archivo `verificar_datos.py` cuenta los registros cargados y agrupa las publicaciones por usuario. Las pruebas cubren la estructura de una publicación, una respuesta vacía y una falla de conexión. Ejecuté el pipeline completo y cargué 100 publicaciones; la consulta confirmó los 100 registros y mostró diez publicaciones para cada uno de los cinco primeros usuarios. Ruff pasó sin errores, las pruebas pasaron y el formato quedó verificado.

### Una decision de diseño, explicada

Elegí la disposición `replace` porque cada ejecución representa una descarga completa de las publicaciones y debe reflejar el estado actual de la API. Una disposición `append` duplicaría las publicaciones al repetir el pipeline, mientras que `merge` exigiría una clave y una regla de actualización más complejas para este ejemplo. También elegí JSONPlaceholder porque permite probar una API real sin administrar credenciales ni datos personales.

Confié en el esquema automático de dlt para traducir los campos del JSON a columnas y tipos de DuckDB. Validé antes de cargar que el cuerpo fuera una lista, pero no cambié manualmente los nombres de los campos. Esta decisión reduce el código repetitivo y permite observar cómo dlt interpreta una estructura JSON estable; mantuve la verificación SQL separada para confirmar el resultado de forma observable.

### Un problema que apareció

Al principio, el entorno no tenía disponibles `dlt` ni `duckdb`, y una sincronización completa encontró una descarga de PyPI que no pudo completarse por una falla de red. Intenté resolverlo con el flujo completo del proyecto, pero las dependencias del entorno bloqueaban la ejecución. La solución fue realizar una instalación dirigida de las librerías mínimas requeridas por este pipeline. Después de reinstalar, el pipeline pudo ejecutarse y las pruebas pudieron importar sus módulos.

Otra revisión importante fue distinguir los datos entregados del recurso generado. El archivo `data.duckdb` se crea al ejecutar el pipeline, por lo que no debe confundirse con el código fuente de la entrega. Conservé los archivos Python y el informe como fuente reproducible y eliminé la base generada antes de preparar los commits, ya que cada ejecución puede recrearla.

### Que haría distinto con mas tiempo

La primera mejora sería separar la obtención HTTP de la configuración del recurso y usar datos simulados más completos en las pruebas. También agregaría paginación o un límite configurable, comprobaría tipos y campos obligatorios antes de entregar las filas a dlt, y guardaría una muestra local para ejecutar las pruebas sin Internet. Con más tiempo añadiría una consulta de duplicados, una verificación de valores nulos y una comprobación explícita de que cada campo conserva el tipo esperado.

### Ayudas externas

Consulté la documentación habitual del proyecto y usé GitHub Copilot para organizar el código, las pruebas y este informe. Verifiqué la sintaxis, ejecuté el pipeline completo y revisé los resultados de la consulta SQL. Las decisiones técnicas, los datos observados y la revisión final siguen siendo responsabilidad mía.
