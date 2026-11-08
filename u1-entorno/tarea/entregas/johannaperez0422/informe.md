# Informe de unidad 1

---

## Unidad: [1. Entorno de trabajo y reproducibilidad]
 

**Nombre: Deysi Johanna Pérez Lesmo**

**Fecha: 17/10/2026**

**Tag de cierre: u1-completa** 
 

### Que se hizo

El trabajo consistió en preparara el entorno del curso, corregir un ejercicio de Python y comprobar como se comportaba aplicando pruebas automatizadas. Comencé creando un fork del repositorio de ciencia_datos y abrí mi copia en Github Codespaces, seguidamente preparé la rama de la unidad y una carpeta personal para la entrega, donde copié el ejercicio original para trabajar sobre él.
Ejecuté Ruff para poder identificar problemas de estilo y aplicar las correciones automáticas disponibles. Después resolví los ajustes pendientes, nombre de funciones con minúsculas, corrección de comparación con None, eliminé variable sin uso, pecisé las excepciones y corregí el argumento mutable. Finalmente agregé cuatro pruebas y ejecuté las comprobaciones de estilo y funcionamiento.

### Entorno

Trabaje dentro del contenedor de Codespaces con Python 3.12.11. como no soy muy técnica decidí volver a analizar los videos de la clase, y la aplicación de la herramienta de AI Openai para algunas cuestiones más complejas, que escapan de mi conocimiento, para ello, me informó que realice la configuración que ejecuta uv sync --all-groups para instalar las dependencias del proyecto, la primera verificación que se realizó, detectó que faltaba pre-commit y obtuve la versión 4.7.0. Tras repetir verificar_entorno.py, y así el programa terminó con OK. 
Para repetir esta instalación adicional, fijé pre-commit==4.7.0 en requeriments-entorno.txt dentro de mi carpeta. Después de preparar el contenedor puede instalar mediante el siguiente comando: 

uv pip install -r u1-entorno/tarea/entregas/johannaperez0422/requeriments-entorno.txt

### Flujo de git

Aquí junto la herramienta de IA me indicó que utilicé la rama u1/johannaperez0422. para que pudiera organizar los cambios en commits diferenciados como conservar el ejercicio inicial, corregirlos y agregar las pruebas, permitiendo revisar revisar la evolución del trabajo y relacionar cada registro con una finalidad concreta. Seleccioné los archivos mediante rutas específicas para mantener los commits dentro de mi carpeta de entrega. 

el archivo uv.lock apareció modificado durante la preparación del entorno; quedó fuera de los commits de entrega. La contribución destinada es un pull request al repositorio original, conservando ese enlace. 


### Una decisión de diseño, explicada

La decisión principal fue reemplazar acumulado={} por acumulado=None en resumen_por_marca, el diccionario predeterminado podía conservar modficaciones entre llamadas independientes y mezclar ventas de distintas ejecuciones. Con None, creó un diccionario nuevo cuando no recibe un acumulador, cuando se proporciona uno de forma explícita conserva la posibilidad de acumular sobre ese objeto. 

La prueba de llamadas indpendientes comprueba esta decisión: procesa Toyota y Ford en ejecuciones separadas y verifica ambos resultados después de la segunda llamada, así puede detectar la contaminación del primer resultado, además de revisar el segundo. 

### Un problema que apareció

La preparación inicial no incluyó un pre-commit, aunque el verificador lo exigía, una vez que se instaló de forma adicional, se pudo completar la comprobación, también sucedió una desconexión momentanea de Codespaces,lo que me generó ligera angústia por la posibilidad de perder lo poco que había aportado, pero luego la IA me mostró como comprobar que la rama seguía disponible y continué con la revisón del arhivo.

### Ayudas externas 

Pero Ruff apareció con cinco advertencias después del formato automático, la IA me indicó que realizara los cambios manuales, los identifiqué y lo hice, guardé el archivo y repetí la comprobación hasta que obtuve ALL CHECKS PASSED, luego pytest informó cuatro pruebas aprobadas con el resultado de 4 passed en 0.04 segundos, verificando el redondeo de comisión, la suma por marca, la lista vacía como caso borde y la independencia entre llamadas. 


### Que harías distinto con mas tiempo  
Estudiaría más la parte técnica del lenguaje Python, hay algunas denominaciones que aún no domino. 

### Reflexión

Si bien entiendo que es lo que exactamente se debe mofificar, ajustar, o eliminar, los palabras técnicas más elaboradas para poder completar la inferencia. 

