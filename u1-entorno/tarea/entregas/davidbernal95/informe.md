# Informe de unidad

## Unidad: 1 — Mi primer aporte reproducible

**Nombre:** Joel Bernal 
**Fecha:** 16/10/2026
**Tag de cierre:** u1-completa

### Que se hizo

Creé un fork del repositorio del curso y abrí el proyecto en GitHub Codespaces. Activé el entorno virtual y ejecuté verificar_entorno.py para comprobar las herramientas disponibles. Después creé la rama u1/davidbernal95 y copié ejercicio.py a mi carpeta de entrega, conservando el archivo original del curso.

Ejecuté Ruff para aplicar correcciones automáticas de estilo y formato. Con asistencia de ChatGPT completé los cambios manuales: eliminé importaciones y variables sin uso, renombré ParseFecha como parse_fecha, corregí la comparación con None y reemplacé el except general por excepciones específicas. También corregí el acumulador de resumen_por_marca.

Preparé tres pruebas con pytest. Comprueban la suma de precios por marca, el comportamiento con una lista vacía y la independencia entre llamadas. La ejecución terminó con tres pruebas aprobadas. Ruff también mostró All checks passed. Finalmente, registré la versión de pre-commit en un archivo de dependencias dentro de mi carpeta.

### Una decisión de diseño, explicada

La decisión principal fue sustituir el diccionario predeterminado de resumen_por_marca por None. Los argumentos predeterminados de Python se evalúan al definir la función. Por eso, un diccionario colocado directamente en los parámetros puede conservar datos entre llamadas y mezclar ventas de ejecuciones diferentes.

Ahora se crea un diccionario nuevo cuando no se proporciona un acumulador. Si se recibe uno explícitamente, se utiliza para continuar sumando. Así se evita compartir información por accidente y se mantiene la posibilidad de acumular resultados de manera intencional.

### Un problema que apareció

La primera comprobación del entorno falló porque faltaba pre-commit. Instalé la herramienta con uv y repetí el verificador hasta obtener OK dentro de Codespaces. Después guardé pre-commit==4.7.0 en requirements.txt para poder repetir esa instalación con la misma versión.

También apareció una modificación de uv.lock fuera de mi carpeta de entrega. Guardé una copia de respaldo y restauré la versión original para respetar el alcance solicitado. Los cambios registrados quedaron dentro de mi carpeta.

El problema del diccionario compartido quedó cubierto por una prueba que realiza dos llamadas consecutivas. El segundo resultado debe contener únicamente Ford, aunque la primera llamada haya procesado Toyota. La prueba con una lista vacía cubre el caso borde y espera un diccionario vacío.

### Que harías distinto con mas tiempo

Ampliaría las pruebas para cubrir fechas inválidas, nombres sin identificador y diferentes comisiones. También revisaría con el docente la incorporación de pre-commit a la configuración compartida del contenedor, porque actualmente requiere una instalación adicional.

### Entorno

Trabajé con Python 3.12.11, pytest 9.1.1, Ruff 0.16.10, pre-commit 4.7.0 y Git 2.50.1. El contenedor instala las dependencias del proyecto mediante uv. La dependencia adicional se instala ejecutando, desde la raíz del repositorio, `uv pip install -r u1-entorno/tarea/entregas/davidbernal95/requirements.txt`. Después se puede repetir el verificador para confirmar el entorno.

### Flujo de Git

Utilicé una rama propia y registré tres avances separados: la corrección del ejercicio, las pruebas y la dependencia fijada. Los mensajes explican el propósito de cada cambio. Este informe se guardará en un cuarto commit.

La entrega está en u1-entorno/tarea/entregas/davidbernal95/. Antes de publicarla corresponde ejecutar el validador, comprobar el alcance de los cambios y crear el tag u1-completa. La apertura del pull request al repositorio del curso está pendiente al redactar este documento.

### Reflexión

Las comprobaciones realizadas muestran que revisar el estilo y probar el comportamiento son tareas complementarias. Ruff permite detectar inconsistencias del código, mientras que pytest compara resultados concretos con lo esperado. El caso del acumulador demuestra por qué conviene probar varias llamadas y entradas vacías, además de ejemplos habituales.

### Ayudas externas

Utilicé ChatGPT para recibir instrucciones paso a paso, interpretar mensajes y preparar las correcciones, las pruebas y este borrador. Ejecuté los comandos en mi Codespace y compartí capturas de los resultados. La entrega requiere mi revisión personal y poder explicar cada línea presentada.