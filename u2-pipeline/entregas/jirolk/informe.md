# Informe de unidad: U2, primer pipeline con dlt y DuckDB

**Nombre:** Sandro Roberto Castillo Delgado

**Usuario:** jirolk

**Fecha:** 2026-10-25

## Entorno

Preparé la implementación sobre la rama `u2/jirolk` y partí del repositorio fork ya configurado. El proyecto declara `dlt[duckdb]`, `duckdb`, `pytest` y `ruff` en `pyproject.toml`; por ello sincronicé las dependencias necesarias dentro del entorno virtual y comprobé las versiones disponibles. Un primer intento encontró una falla temporal al descargar paquetes de PyPI, pero un intento dirigido posterior logró instalar las dependencias mínimas. La ejecución final confirmó 100 publicaciones en DuckDB, tres pruebas aprobadas y Ruff en verde.

La entrega usa una API pública de JSONPlaceholder para obtener publicaciones. Elegí esta fuente porque no requiere autenticación, devuelve JSON estable y permite demostrar extracción, carga, persistencia y consulta sin guardar claves. La ruta de la base de datos se calcula a partir del propio archivo de entrega, por lo que `data.duckdb` se genera siempre dentro de la carpeta correcta y el proyecto no depende de una ruta absoluta de mi equipo.

## Diseño del pipeline

El archivo `pipeline.py` contiene la extracción y la carga. La función `obtener_publicaciones` usa `urllib.request`, convierte el cuerpo JSON y valida que el resultado sea una lista. Los errores HTTP, de DNS o de red se transforman en excepciones con mensajes comprensibles. El recurso decorado con `@dlt.resource` recibe una colección de publicaciones o solicita la API si no se le proporciona una. La opción `replace` hace que cada ejecución reconstruya el contenido de la tabla, evitando duplicados por ejecuciones repetidas del pipeline.

El pipeline se configura con el nombre `jsonplaceholder_posts`, el destino DuckDB y el esquema `u2_posts`. La tabla generada se llama `posts` por el nombre definido en el recurso. La carga no mezcla transformaciones manuales con el esquema: dlt normaliza el JSON y conserva los campos `user_id`, `id`, `title` y `body`. Antes de cargar, se puede pasar explícitamente una lista vacía para comprobar el comportamiento del recurso sin realizar una llamada de red.

## Verificación de datos

El script `verificar_datos.py` abre `data.duckdb` en modo de solo lectura. Primero cuenta los registros de `u2_posts.posts`, luego agrupa las publicaciones por `user_id` para mostrar los cinco autores con mayor cantidad. Esto confirma tanto que los datos existen como que la tabla sigue un esquema consultable. El verificador falla de manera explícita si la base de datos todavía no fue creada, evitando una consulta confusa después de ejecutar el pipeline.

Las pruebas cubren la estructura de una publicación, una respuesta vacía y una excepción de conexión. La primera prueba confirma que los campos esperados llegan al recurso. La segunda evita que una lista vacía se trate como un error. La tercera simula una falla de DNS y verifica el mensaje de usuario. Estas pruebas ayudan a separar errores de extracción de problemas de carga sin depender necesariamente de Internet.

## Reflexión

dlt simplifica el recorrido entre una respuesta JSON y una tabla persistente: el esquema emerge de los datos y la carga se decide de forma declarativa. Esta automatización es útil, pero mantiene la responsabilidad de validar tipos, nombres y estructura antes de analizar. DuckDB ofrece una ventaja práctica al permitir consultas SQL locales y rápidas sin instalar un servidor separado.

En una iteración futura separaría aún más la función de transporte, permitiría configurar límites o paginación y haría pruebas sobre tipos de datos inferidos por dlt. También guardaría una muestra o un fixture de datos cuando la red estuviera disponible, para hacer verificaciones completamente reproducibles. Usé herramientas de IA para revisar estructura y mensajes de código, pero ejecuté las decisiones y entendí cada etapa del flujo.

## Ayudas externas

Consulté la documentación habitual del proyecto y usé GitHub Copilot para organizar el código, las pruebas y este informe. Verifiqué la sintaxis, ejecuté el pipeline completo y revisé los resultados de la consulta SQL. Las decisiones técnicas, los datos observados y la revisión final siguen siendo responsabilidad mía.
