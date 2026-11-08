# Informe de unidad
 
## Unidad: 1 - Entorno reproducible y primer aporte
 
**Nombre:** Diana More Facet
**Fecha:** 18/10/2026
**Tag de cierre:** u1-completa
 
## Qué se hizo
 
Para realizar la actividad se creó el usuario **dianamorefacet** y se generó un fork del repositorio **curso-datos**. A continuación se creó la rama **u1/dianamorefacet**, donde se desarrolló todo el trabajo solicitado.
 
La actividad se realizó utilizando GitHub Codespaces. Luego de iniciar el entorno, se activó el entorno virtual mediante `source .venv/bin/activate` y se verificó su correcto funcionamiento ejecutando el script de validación proporcionado por la cátedra.
 
Dentro de `u1-entorno/tarea` se creó el directorio `entregas/dianamorefacet`. En esta carpeta se copiaron los archivos requeridos para la entrega y posteriormente se creó el archivo `test_ejercicio.py` con las pruebas automatizadas.
 
Se ejecutaron las herramientas `ruff check --fix` y `ruff format` sobre `ejercicio.py` para corregir problemas de estilo y formato. Después se realizaron ajustes manuales para resolver observaciones que requerían intervención del desarrollador sin modificar el comportamiento esperado de las funciones.
 
## Entorno
 
El uso de GitHub Codespaces permitió trabajar en un entorno reproducible y homogéneo. Esto redujo posibles diferencias entre equipos y evitó tareas adicionales de instalación o configuración local.
 
La validación inicial del entorno permitió confirmar que todas las dependencias necesarias estaban disponibles antes de comenzar las modificaciones. Esto facilitó el desarrollo y ayudó a evitar problemas relacionados con la configuración del sistema.
 
## Una decisión de diseño, explicada
 
La principal decisión de diseño fue modificar la función `resumen_por_marca` para utilizar `None` como valor por defecto del parámetro `acumulado`.
 
La implementación original utilizaba un diccionario mutable como valor por defecto. Aunque el resultado parecía correcto en ejecuciones aisladas, este enfoque puede provocar que diferentes llamadas compartan información de manera involuntaria.
 
Para validar el comportamiento esperado se desarrolló una prueba que invoca la función varias veces sin proporcionar el parámetro `acumulado`. Gracias a esta prueba fue posible comprobar que cada ejecución utiliza un diccionario independiente.
 
## Flujo de Git
 
El trabajo se realizó íntegramente sobre la rama `u1/dianamorefacet`. Los cambios se organizaron mediante varios commits pequeños y descriptivos para facilitar la revisión del historial.
 
Primero se preparó la estructura de entrega. Luego se aplicaron las correcciones al código, posteriormente se incorporaron las pruebas unitarias y finalmente se completó la documentación requerida para la actividad.
 
Este enfoque permitió mantener una trazabilidad clara de los cambios realizados durante el desarrollo.
 
## Un problema
 
El principal problema identificado estuvo relacionado con el uso de un parámetro mutable como valor por defecto en `resumen_por_marca`.
 
Este tipo de error no siempre es evidente, ya que puede permanecer oculto mientras la función se utiliza en escenarios simples. La creación de una prueba específica permitió detectar este comportamiento y confirmar la necesidad de modificar la implementación.
 
Una vez realizada la corrección, la función pasó a comportarse de manera consistente entre llamadas consecutivas.
 
## Reflexión
 
La actividad permitió practicar conceptos relacionados con entornos reproducibles, análisis estático de código, pruebas automatizadas y control de versiones. También ayudó a comprender que una aplicación puede parecer correcta y aun así contener errores que solamente se revelan mediante pruebas adecuadas.
 
Además, se utilizó Microsoft Copilot como herramienta de apoyo para aclarar dudas sobre Python, comprender algunas recomendaciones de Ruff y proponer ideas para las pruebas con pytest. Sin embargo, todas las sugerencias fueron revisadas y validadas antes de ser incorporadas al proyecto.
 
## Ayudas externas
 
Se consultó la documentación oficial de Python y Ruff para comprender mejor las advertencias detectadas y verificar buenas prácticas relacionadas con excepciones, parámetros por defecto y pruebas unitarias.
 
También se utilizó Microsoft Copilot como apoyo para la comprensión de conceptos y la elaboración de casos de prueba. Las respuestas obtenidas fueron utilizadas únicamente como orientación y siempre fueron revisadas antes de su aplicación.
 
## Qué haría distinto con más tiempo

Con más tiempo ampliaría la cobertura de pruebas incorporando casos adicionales con entradas inválidas, valores vacíos y distintos escenarios límite. También implementaría un flujo de integración continua para ejecutar automáticamente las pruebas y las verificaciones de calidad cada vez que se realizara un commit o se abriera un pull request.