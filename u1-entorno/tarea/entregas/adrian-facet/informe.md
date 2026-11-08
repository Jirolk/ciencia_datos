# Informe de unidad

## Unidad: 1 — Mi primer aporte reproducible

**Nombre:** adrian-facet  
**Fecha:** 18/10/2026  
**Tag de cierre:** u1-completa

### Qué se hizo

Abrí el repositorio del curso en GitHub Codespaces y preparé el entorno de trabajo. La primera vez que ejecuté el verificador, indicó que faltaba pre-commit. Intenté instalarlo con pip, pero el entorno virtual no tenía ese módulo. Entonces utilicé `uv pip install pre-commit` y volví a ejecutar la verificación. Esta vez terminó con `OK`, así que pude continuar con la actividad.

Después creé la rama `u1/adrian-facet` y la carpeta de entrega correspondiente a mi usuario. Copié allí el ejercicio original y ejecuté Ruff para revisar el estilo y aplicar las correcciones automáticas disponibles. También corregí manualmente los problemas que Ruff no resolvía, como el nombre de la función para interpretar fechas, la comparación con `None` y el uso de una excepción demasiado general.

Luego preparé pruebas con pytest. Incluí una fecha válida de año bisiesto, un caso en que el texto no tiene identificador y una comprobación del resumen de ventas por marca. Ejecuté las pruebas y las tres pasaron. También revisé el estilo y el formato de los archivos de la carpeta de entrega.

### Una decisión de diseño, explicada

En `resumen_por_marca`, cambié el argumento `acumulado` para que su valor inicial sea `None` y no un diccionario vacío. En Python, los argumentos predeterminados se crean cuando se define la función. Si se usa un diccionario vacío como valor predeterminado, ese mismo objeto puede reutilizarse entre llamadas. Como resultado, una llamada podría conservar datos de una anterior y producir un resumen inesperado.

Para evitarlo, la función crea un diccionario nuevo cuando no recibe un acumulado. Si se le pasa uno, puede seguir utilizándolo para sumar las nuevas ventas. Elegí este cambio porque mantiene el propósito de la función y evita que sus resultados dependan de llamadas anteriores. La prueba que llama dos veces a la función con las mismas ventas ayuda a comprobar ese comportamiento.

### Un problema que apareció

El problema principal ocurrió al preparar el entorno. El verificador informó que faltaba pre-commit, pero `python -m pip install pre-commit` no funcionó porque pip no estaba disponible dentro del entorno virtual. La herramienta `uv` sí estaba disponible, así que instalé pre-commit con ella y repetí la verificación.

También encontré advertencias que requerían cambios manuales. Ruff señaló, entre otros puntos, que el nombre `ParseFecha` no seguía la convención de nombres, que se comparaba con `None` usando `==` y que se utilizaba un `except` sin especificar el tipo de error. Corregí esos casos y volví a ejecutar las revisiones y las pruebas.

### Qué haría distinto con más tiempo

Con más tiempo, ampliaría las pruebas para cubrir cada función y varios casos límite. Por ejemplo, probaría una fecha inválida, precios que no se puedan convertir a número y una lista de ventas con más de una marca. También comprobaría qué sucede si falta una clave necesaria en uno de los diccionarios de venta.

Además, revisaría la documentación de cada función para aclarar cómo debe comportarse ante datos incompletos o incorrectos. Eso haría que el código fuera más fácil de usar y que las pruebas dejaran más claro qué resultados se esperan. Después de guardar el informe, comprobaré que la carpeta contiene los tres archivos pedidos y que el informe tiene entre 500 y 700 palabras.

## Entorno

El entorno quedó verificado con Python 3.12.11, pytest 9.1.1, Ruff 0.16.10 y pre-commit 4.7.0. Después de instalar pre-commit usando uv, el verificador terminó con OK.

## Flujo de Git

Trabajé en la rama `u1/adrian-facet`. Separé los cambios en commits para corregir el ejercicio y agregar pruebas. Ahora registraré el informe en su propio commit. Preparé la entrega dentro de la carpeta correspondiente a mi usuario.

## Reflexión

Aprendí que verificar el entorno y probar el código ayuda a encontrar problemas antes de compartir una entrega. También comprendí por qué un argumento predeterminado mutable puede afectar llamadas posteriores.

## Ayudas externas

Usé la IA para entender los mensajes de la terminal y recibir orientación sobre la estructura del informe. Revisé las indicaciones y ejecuté las correcciones y pruebas en Codespaces.