# Informe de unidad

## Unidad: 2 - Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Joel Bernal
**Fecha:** 25/10/2026
**Tag de cierre:** u2-completa

### Que se hizo

La solución consulta las publicaciones de JSONPlaceholder mediante una solicitud HTTP con tiempo límite. Comprueba que la respuesta sea una lista no vacía y que cada publicación contenga identificador, usuario, título y cuerpo con los tipos esperados. El recurso extraer_posts entrega esos registros a dlt, que los normaliza y carga en data.duckdb, dentro del esquema jsonplaceholder y la tabla posts.

El segundo script abre la base en modo de solo lectura y ejecuta consultas SQL. Comprueba el total, describe las columnas, agrupa publicaciones por usuario y muestra cinco ejemplos. La ejecución real obtuvo 100 publicaciones, distribuidas entre diez usuarios con diez publicaciones cada uno. La consulta funciona en un proceso separado, lo que permite comprobar la persistencia del archivo.

### Una decisión de diseño, explicada

El recurso utiliza replace porque esta API entrega una colección completa. Una nueva ejecución reemplaza la carga anterior y evita sumar otra copia de los mismos registros. La prueba de integración ejecuta el pipeline dos veces y comprueba que permanezcan dos filas de ejemplo, en lugar de cuatro. El identificador id se declara como clave del recurso, sin asumir que esa declaración elimina cualquier duplicado dentro de la respuesta.

La validación ocurre antes de cargar. Una lista vacía produce un error explícito para evitar tratar una respuesta inesperada como una extracción satisfactoria. Los errores HTTP y de conexión también interrumpen la ejecución. El código conserva la inferencia automática de dlt: los identificadores quedaron como BIGINT y los textos como VARCHAR. Además, dlt normalizó userId a user_id y añadió sus columnas de seguimiento. La consulta SQL utiliza los nombres observados en DuckDB.

### Un problema que apareció

Al comenzar, el archivo propio del pipeline estaba abierto como un documento sin guardar. La terminal indicó que no existía en la ruta de entrega. La solución fue crear el contenido y guardarlo realmente dentro de entregas/davidbernal95, diferenciándolo del ejemplo del profesor en lab-ingesta.

Otro aspecto importante fue aislar las pruebas de la disponibilidad de internet. Las respuestas simuladas permiten probar conexiones fallidas, errores HTTP, estructuras inválidas y una lista vacía de manera repetible. La prueba de persistencia utiliza una base temporal real, mientras que la comprobación de la API pública se ejecuta por separado.

### Que harías distinto con mas tiempo

Agregaría controles explícitos de identificadores repetidos y una estrategia de cambios de esquema para nuevas columnas o tipos incompatibles. Para una API paginada, incorporaría el recorrido de todas sus páginas. Para conservar historial entre ejecuciones, evaluaría merge o tablas con fecha de extracción, en lugar de reemplazar siempre la colección completa.

### Entorno y evidencias

Las versiones están fijadas en requirements.txt: dlt 1.30.0, DuckDB 1.5.6, pytest 9.1.1 y Ruff 0.16.10. En el contenedor Linux de Codespaces, con Python 3.12.11, se aprobaron once casos de prueba y los controles de estilo y formato. comprobar_entrega.py repite esos controles, ejecuta la carga y guarda en evidencias.json las versiones, los resultados y el esquema consultado. SQL confirmó 100 registros persistidos.

### Flujo de Git

La rama es u2/davidbernal95. Los commits separan la extracción y carga, las consultas de verificación, las pruebas, el control reproducible y la documentación con sus evidencias. Solo se agregan archivos dentro de la carpeta de entrega. La base generada y el estado temporal de dlt se excluyen mediante un archivo .gitignore propio. El tag u2-completa identifica la versión presentada para revisión.

### Reflexión y ayudas externas

DuckDB facilita comprobar resultados sin administrar un servidor y permite volver a abrir el archivo desde otro programa. Su comodidad no reemplaza la validación de entrada ni la necesidad de revisar el esquema generado. Esta solución utiliza datos ficticios y no pretende cubrir todos los problemas de una API productiva.

Se utilizó ChatGPT como apoyo durante la implementación, las pruebas y la documentación. También se consultaron las documentaciones oficiales de dlt, DuckDB y JSONPlaceholder. La ayuda de IA queda declarada; corresponde revisar esta reflexión y poder explicar cada línea antes de presentar la entrega.
