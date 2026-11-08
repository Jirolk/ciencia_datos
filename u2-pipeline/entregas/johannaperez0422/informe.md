# Informe U2: Mi primer pipeline con dlt y DuckDB I_I

**Estudiante:** Deysi Johanna Pérez Lesmo  
**Usuario GitHub:** johannaperez0422  
**Rama:** `u2/johannaperez0422`

## Entorno y organización

Para esta actividad utilicé el mismo Codespace de la primera tarea, con el entorno virtual del repositorio. Al inicio me resultó confuso identificar dónde trabajar, porque relacionaba todo lo visible con la entrega anterior y tenía preocupación por modificarla. Mediante orientación pude ubicar la nueva rama y la carpeta `u2-pipeline/entregas/johannaperez0422`. Antes del cambio de rama, guardé temporalmente la modificación pendiente de `uv.lock` mediante `git stash`. Esto permitió continuar conservando ese cambio y manteniendo separadas las entregas.

## Diseño del pipeline

El pipeline consulta el endpoint `/posts` de JSONPlaceholder, una API pública de datos ficticios que no requiere credenciales. La solución utiliza un recurso de dlt llamado `publicaciones`, que solicita los datos y comprueba que la respuesta sea una lista no vacía y que cada registro contenga los campos esperados. Una respuesta vacía o incompleta detiene la extracción antes de cargarla.

La configuración establece DuckDB como destino, `api_publica` como esquema y `publicaciones` como tabla. El archivo `data.duckdb` queda dentro de mi carpeta de entrega. Se utiliza `write_disposition="replace"`, porque se recupera una colección completa: al repetir la ejecución se reemplaza el contenido de la tabla y se evita acumular las mismas publicaciones. La base y el estado local de dlt están excluidos del seguimiento de Git mediante `.gitignore`.

## Esquema automático y consultas

En esta implementación no se escribió manualmente una sentencia para crear la tabla. dlt infirió el esquema a partir de los registros recibidos. Al ejecutar `verificar_datos.py`, observé que `userId` se normalizó como `user_id`; este campo y `id` quedaron como `BIGINT`, mientras que `title` y `body` quedaron como `VARCHAR`. También aparecieron las columnas de seguimiento `_dlt_load_id` y `_dlt_id`.

El verificador abre la base en modo de solo lectura y ejecuta consultas SQL. El resultado mostró 100 publicaciones en total y 10 correspondientes al usuario 1, además de los primeros cinco registros y los tipos de las columnas. Consultar los datos mediante otro programa permitió comprobar que quedaron almacenados después de finalizar el pipeline. Esta fue mi primera aproximación práctica a DuckDB dentro de la actividad, por lo que todavía necesito familiarizarme más con sus posibilidades y limitaciones.

## Pruebas y resultados

Ejecuté las pruebas con pytest y obtuve `6 passed in 1.64s`. Se comprobaron la estructura del recurso, las respuestas vacías o incompletas, un error de conexión simulado y la persistencia sin duplicados después de dos cargas. Estas pruebas utilizan respuestas simuladas y una base temporal. Además, ejecuté Ruff: la revisión indicó `All checks passed!` y la comprobación de formato informó `3 files already formatted`.

## Reflexión y ayudas externas

Durante el proceso comprendí mejor el seguimiento de los pasos y las razones de ciertos fragmentos de código necesarios para ejecutar la tarea. También me estoy adaptando al entorno de trabajo de GitHub, aunque aún necesito conocer mejor sus posibilidades y limitaciones. La organización por ramas me ayudó a distinguir las actividades dentro del mismo repositorio.

Todavía me resulta confusa la escritura técnica del código. Si bien entiendo lo que necesito realizar, aún no acompaño por completo el lenguaje de programación. Lo relaciono con aprender un nuevo idioma: mediante la práctica y la escritura constante podré desenvolverme mejor, así también tuve varios inconvenientes con la conexión. 

Utilicé ChatGPT/Codex para interpretar la consigna, preparar el código y las pruebas, organizar la rama y los commits, y recibir orientación sobre los comandos y resultados, mismo para no perder lo que avanzaba tras los cortes. También recibí ayuda para redactar los detalles más técnicos dentro de este informe. Mi participación consistió en ejecutar los pasos en Codespaces, revisar las salidas y expresar mis dudas y aprendizajes, sinceramente es la primera vez que comienzo a comprender cada pestaña y formato de archivo para el entorno. Actualmente la IA me acompaña en la escritura del código, mientras continúo desarrollando mi autonomía.
