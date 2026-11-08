# Informe de unidad 1: Entorno reproducible y Git
Informe técnico acotado para el cierre de cada unidad
---
## Unidad: U1 - Entorno reproducible y flujo de trabajo colaborativo
**Nombre:** [Luis Mello]
**Fecha:** 18 de octubre de 2026
**Tag de cierre:** `u1-completa`

## Entorno
Para garantizar la reproducibilidad científica y el aislamiento del proyecto, el trabajo se inició bifurcando (*fork*) el repositorio `ciencia-datos` hacia mi cuenta personal de GitHub y levantando un entorno de desarrollo estructurado con GitHub Codespaces (Dev Container). 


## Flujo de Git
El trabajo se desarrolló siguiendo una metodología orientada a la reproducibilidad científica y las buenas prácticas de desarrollo en Python:
1. **Bifurcación y entorno:** Se realizó un *fork* del repositorio `ciencia-datos` hacia mi cuenta personal de GitHub y se inicializó un entorno de desarrollo reproducible mediante GitHub Codespaces (Dev Container).
2. **Activación y verificación:** Se activó el entorno virtual aislado (`source .venv/bin/activate`). Al ejecutar `python u1-entorno/tarea/verificar_entorno.py`, se identificó la ausencia de dependencias necesarias (`pre-commit`), las cuales se instalaron mediante `pip install -r requirements.txt`, logrando el estado de verificación en verde (`OK`).
3. **Control de versiones:** Se creó la rama de trabajo `u1/1534393` y la estructura de carpetas personal `u1-entorno/tarea/entregas/1534393/`.
4. **Refactorización de código:** Se copió `ejercicio.py` y se analizó con `ruff check --fix` y `ruff format`. Se corrigieron manualmente los errores que el linter no resuelve por defecto: ajuste a convención snake_case (`parse_fecha`), reemplazo de comparaciones con `is None`, eliminación de variables muertas, inicialización segura de estructuras mutables y captura explícita de excepciones. Esto constituyó el primer commit.
5. **Pruebas unitarias:** Se implementó `test_ejercicio.py` con Pytest, cubriendo casos típicos y casos de borde (listas vacías y valores en cero), validando la totalidad de pruebas con éxito (`3 passed`). Esto conformó el segundo commit.
6. **Validación final:** Se comprobó la entrega localmente mediante `validar_entrega.py` antes de redactar este informe técnico (tercer commit) y abrir el Pull Request.

## Reflexión
Una de las decisiones centrales de diseño fue la resolución del error `B006` en la función `resumen_por_marca(ventas, acumulado=None)`. 
El código original utilizaba un diccionario vacío como argumento por defecto: `acumulado={}`. En Python, los argumentos por defecto son evaluados una sola vez cuando la función se define, no cada vez que se invoca. Si se muta una estructura de datos mutable pasada por defecto, ese mismo objeto persiste en memoria entre llamadas consecutivas, generando efectos secundarios y rompiendo el principio de idempotencia y pureza funcional.
Para solucionar esto de raíz, se definió `acumulado=None` como valor por defecto y se implementó la inicialización interna:
```python
if acumulado is None:
acumulado = {}

Con este patrón se garantiza que cada ejecución de la función opere sobre una instancia nueva e independiente de la memoria, asegurando la reproducibilidad de los cálculos. Asimismo, se diseñó la prueba unitaria de caso borde test_resumen_por_marca_caso_borde_lista_vacia, verificando que una entrada vacía retorne un diccionario limpio {} sin anomalías.
## Un problema que apareció
Durante el desarrollo surgieron dos dificultades técnicas concretas que requirieron diagnóstico y corrección:
1.	Dependencias faltantes en el entorno virtual:
Al ejecutar inicialmente el script de verificación, el sistema alertó que pre-commit no estaba instalado en el entorno .venv. La solución consistió en asegurar que el entorno virtual estuviese activo y correr ‘uv pip install pre-commit’. Tras completar la descarga de los paquetes fijados, la reejecución de verificar_entorno.py arrojó el OK requerido.
2.	Convención de nombres en Git (símbolo @):
Al crear la rama y la carpeta de entrega, se utilizó inadvertidamente el prefijo @1534393, guiado por el indicador visual del prompt de la terminal. Sin embargo, en GitHub y en los scripts automatizados de corrección (validar_entrega.py), los identificadores de usuario son estrictamente alfanuméricos y carecen de @. Mantener el @ hubiese provocado el rechazo del Pull Request.
Para resolverlo de forma limpia en el historial de Git, se renombró la rama activa usando git branch -m u1/1534393 y se trasladó el directorio con mv u1-entorno/tarea/entregas/@1534393 u1-entorno/tarea/entregas/1534393.

## Ayudas externas
Para el desarrollo de esta tarea se consultó la documentación oficial de Python. Asimismo, se utilizó la asistencia de un modelo de inteligencia artificial como tutor interactivo para la resolución de dudas sobre la sintaxis de Git, la interpretación de las alertas de los linters. Todas las decisiones técnicas, comandos ejecutados y comprobaciones en el contenedor fueron revisados, comprendidos y validados personalmente.

##  Que harías distinto con más tiempo
Con mayor tiempo disponible, investigaría más el uso de entorno de Git y GitHub.
