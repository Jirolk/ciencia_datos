# Informe de unidad 2: Pipeline de datos con dlt y DuckDB

Informe técnico de extracción, inferencia de esquema y carga analítica.

---

Nombre:Luis Alberto Mello 
Fecha: 25 de octubre de 2026  
Tag de cierre: `u2-completa`  

---

## Entorno

Para el desarrollo de la Unidad 2 se construyó un pipeline de ingeniería de datos (EL: Extract and Load) completamente funcional y reproducible. El objetivo central consistió en extraer información estructurada desde una API pública, orquestar la ingesta mediante la librería moderna `dlt` (data load tool) y persistir los registros en formato columnar utilizando `DuckDB` en un archivo local denominado `data.duckdb`.

El pipeline (`pipeline.py`) se configuró consumiendo el endpoint `/users` de la API pública JSONPlaceholder. La función generadora se decoró como `@dlt.resource` con la disposición de escritura `write_disposition="replace"`, asegurando que cada corrida refresque el conjunto de datos de forma idempotente y sin duplicaciones indeseadas. 

Posteriormente, se diseñó el script de verificación y consulta analítica (`verificar_datos.py`), el cual se conecta a `data.duckdb` en modo solo lectura (`read_only=True`) y ejecuta sentencias SQL directas (`SELECT COUNT(*)`, ordenamientos y proyecciones) para validar que la información se haya persistido correctamente y que las tablas sean legibles por el motor analítico.

---

## Flujo de Git

El trabajo en el repositorio se gestionó mediante un flujo estricto y ordenado para garantizar un Pull Request limpio:

1. **Ramas independientes:** Se actualizó la rama principal `main` con los cambios remotos y se ramificó a la rama de desarrollo `u2/1534393`.
2. **Commits progresivos y atómicos:** Se dividió el avance en tres confirmaciones claras y descriptivas:
   - Primer commit (`feat`): implementación de `pipeline.py` y `verificar_datos.py`.
   - Segundo commit (`test`): creación de la suite de pruebas unitarias en `test_pipeline.py`.
   - Tercer commit (`docs`): redacción de este informe técnico.
3. **Aislamiento de la entrega:** Todas las operaciones y archivos modificados se mantuvieron confinados de manera exclusiva dentro del directorio `u2-pipeline/entregas/1534393/`.

---

## Reflexión

### Esquema automático y normalización en dlt
Uno de los aspectos más potentes de `dlt` es su capacidad de inferencia y evolución automática de esquemas. Las APIs REST suelen devolver objetos JSON con estructuras anidadas (por ejemplo, el campo `address` que a su vez contiene `geo`, `street`, `city`). En lugar de requerir que el desarrollador defina manualmente tipos de datos rígidos o cree tablas intermedias a mano, `dlt` inspecciona la carga y "aplana" los datos de forma inteligente, creando columnas analíticas limpias como `address__city`. 

Asimismo, al manejar errores durante las pruebas unitarias, se descubrió que `dlt` envuelve las fallas de extracción dentro de su propia excepción `ResourceExtractionError`, preservando la trazabilidad del pipeline cuando la API responde con un código de estado 404 o una falla de red.

### Experiencia con DuckDB
El uso de `DuckDB` demostró ser una solución ideal para entornos embebidos y de ciencia de datos. A diferencia de bases de datos relacionales cliente-servidor como PostgreSQL, no requiere configurar credenciales complejas; opera directamente sobre un archivo local (`data.duckdb`). Al ser un motor columnar, las consultas analíticas sobre los usuarios se resuelven en milisegundos, permitiendo combinar la simplicidad de SQLite con la potencia de procesamiento OLAP.

### Pruebas y casos borde
En `test_pipeline.py` se validó tanto la extracción normal como dos casos límite: la respuesta ante URLs inválidas y la gestión de listas vacías (`[]`) simuladas con `monkeypatch`, verificando que el pipeline reaccione con robustez sin corromper el almacenamiento.

---

## Ayudas externas

Durante el desarrollo de esta unidad se consultó la documentación oficial de `dlt-hub` y la referencia de SQL de `DuckDB`. Además, se utilizó asistencia de inteligencia artificial como soporte de consulta para afinar la captura de excepciones en Pytest y estructurar la redacción del informe para que tenga un tono de redacción técnico/profesional. Cada bloque de código y consulta fue ejecutado, evaluado y comprendido personalmente en el entorno de desarrollo.