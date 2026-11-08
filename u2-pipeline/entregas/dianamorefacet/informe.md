## Informe de unidad

### Unidad: U2: Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** Diana Raquel Moré CI 3.625.595
**Usuario GitHub:** dianamorefacet  
**Fecha:** 25 de Octubre de 2026  
**Tag de cierre:** u2-completa

#### Qué se hizo

En esta unidad desarrollé un pipeline de extracción y carga utilizando Python, dlt y DuckDB. El objetivo fue consumir datos desde la API pública Rick and Morty API, procesarlos y almacenarlos de forma persistente en una base de datos local.

El pipeline obtiene información de los personajes disponibles mediante el sistema de paginación de la API. Posteriormente transforma los datos para conservar únicamente los campos relevantes y los carga en una base de datos DuckDB llamada data.duckdb. Finalmente, los datos pueden consultarse mediante SQL utilizando un script independiente de verificación.

##### Entorno

Trabajé sobre el entorno configurado del codespace del repositorio del curso. Verifiqué el correcto funcionamiento de las dependencias necesarias para la actividad, incluyendo dlt, duckdb, requests y pytest.

También ejecuté las validaciones recomendadas para comprobar que el pipeline funcionara correctamente y que las pruebas unitarias se ejecutaran sin errores.

##### Flujo de Git

Creé la rama de trabajo u2/dianamorefacet y desarrollé la solución dentro de la carpeta asignada para mi usuario. Los cambios fueron registrados mediante commits descriptivos y organizados de manera incremental.

Una vez finalizado el desarrollo preparé el Pull Request correspondiente respetando la restricción de modificar únicamente los archivos de mi carpeta de entrega.

#### Una decisión de diseño, explicada

Elegí trabajar con Rick and Morty API porque ofrece una fuente de datos pública, estable y sencilla de utilizar para una actividad introductoria de ingeniería de datos.

Una decisión importante fue simplificar la estructura de los registros almacenados. La API devuelve información anidada para algunos atributos, como origen y ubicación. En lugar de almacenar los objetos completos, decidí conservar únicamente los nombres asociados a esos campos. Esto permitió generar una tabla más simple y fácil de consultar.

Además, implementé una pausa de 0.5 segundos entre solicitudes consecutivas utilizando time.sleep(). Por medio de esta práctica se realiza un consumo más responsable del servicio.

#### Un problema que apareció

El primer inconveniente estuvo relacionado a un bloqueo por request excesivos, por lo que se solucionó con un sleep de 0.5 segundos entre cada request.

Otro inconveniente surgió durante la implementación de las pruebas unitarias.

Inicialmente esperaba capturar directamente una excepción de tipo ConnectionError cuando simulaba una falla de red mediante mocks. Sin embargo, al ejecutar las pruebas observé que dlt encapsula los errores de extracción dentro de una excepción ResourceExtractionError.

Para resolver este problema adapté la prueba para validar la excepción generada por dlt en lugar de la excepción original. Esta modificación permitió que la prueba reflejara el comportamiento real de la librería y funcionara correctamente en el entorno utilizado.

También implementé pruebas para verificar la estructura de los registros obtenidos, el manejo de respuestas vacías y la validación de tipos de datos. En total se desarrolló una suite de cinco pruebas unitarias.

#### Reflexión y ayudas externas

##### Reflexión

La experiencia permitió comprender mejor el proceso de construcción de pipelines de datos modernos. dlt simplifica gran parte del trabajo relacionado con la extracción y carga de información, mientras que DuckDB ofrece una alternativa ligera para almacenar y consultar datos localmente.

Asimismo, la actividad permitió reforzar conocimientos relacionados con APIs REST, pruebas automatizadas y consultas SQL sobre datos persistidos.

##### Ayudas externas

Para completar la actividad consulté la documentación oficial de dlt, DuckDB, Pytest y Rick and Morty API.

Asimismo, utilicé Microsoft Copilot como herramienta de apoyo para comprender ejemplos de integración con dlt, revisar buenas prácticas de testing, analizar errores relacionados con ResourceExtractionError y mejorar la redacción final del informe. Todo el código entregado fue revisado, comprendido y adaptado antes de su inclusión en la solución final.

#### Qué harías distinto con más tiempo

Con más tiempo implementaría una estrategia de carga incremental para evitar reprocesar todos los registros en cada ejecución. También incorporaría validaciones adicionales de calidad de datos y consultas analíticas más avanzadas para aprovechar mejor las capacidades de DuckDB.

Además, exploraría otros endpoints de la API para ampliar el conjunto de datos disponible y realizar análisis más completos sobre los personajes y sus características.