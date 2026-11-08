# Informe de unidad -- plantilla

Informe técnico acotado para el cierre de cada unidad

---

## Unidad: [1 mi primer aporte reproducible]
 

**Nombre:** [Victor Robles]

**Fecha:**  [12/10/2026]
**Tag de cierre:** (por ejemplo, `u1-completa`)
 

### Entorno

Hice el entregable de la tarea a partir de un fork del repositorio, haciendo los cambios dentro de una rama de git de la que hare pull request, lo primero que hice fue el forck de repo original, luego cree un nuevo codeespace, active el entorno, ejecute verificar_entorno.py, cree la rama u1/VictoRobles, tambien una carpeta con una copia de ejercicios.py que corregi, hice 6 commits y finalmente este informe. lo que se ejecuta es u1-tarea.yml, la revision con ruff, pytest y validar_entrega.py.

### Flujo de Git
Para evitar mezclar mi entrega con otros cambios, partí de main para crear la rama u1/rebekakrauer e incluí una copia de ejercicio.py dentro de entregas/rebekakrauer/. Mantuve un registro transparente organizando la progresión en commits breves y enfocados: la versión base intacta, el autoformato con ruff, la resolución del fallo lógico, los ajustes manuales de estilo, el renombrado funcional, los tests unitarios, la prueba de regresión y el informe final. Dado que el alcance del Pull Request debía limitarse estrictamente a mi carpeta, revertí las modificaciones no deseadas en uv.lock con git restore. Finalmente, la apertura del PR disparó el flujo de CI en u1-tarea.yml para ejecutar ruff, pytest y validar_entrega.py.

### Una decisión de diseño, explicada

Decidi hacer commit separados en vez de un solo comiit con el archivo ejercicio.py ya corregido, hice un commit para el automatico de ruff, otro para b006, otro para avisos restantes, otro para prueba, porque si algo salia mal podia ver exactamente que cambio es lo causo.

### Un problema que apareció

la primera vez que ejecute verifica_entorno.py decia FALTA para pytest, ruff y precommit. Mi terminal usaba el python general asi que ejecute source.venv/bin/activate, pytest y ruff aparecieron, el codespace si la habia instalado pero dentro del entorno. 

### Ayudas externas

Me ayude con un asistente virtual para ayudarme a entender el codigo.

### Reflexión

Lo que más me enseñó esta tarea fue corregir resumen_por_marca. Ruff avisaba de acumulado={}, pero no lo arregla solo, y ahí entendí que no era un problema de estilo: Python crea ese diccionario una sola vez y lo reutiliza en cada llamada, así que la segunda llamada arrastraba los datos de la primera. Lo resolví con acumulado=None y creando el diccionario dentro de la función, porque así cada llamada empieza limpia y la función sigue haciendo lo que dice su descripción. Quitar el parámetro también eliminaba el error, pero cambiaba lo que la función permite hacer.

También cambié el except: de descripcion_venta por except (KeyError, TypeError, ValueError), para atrapar solo los fallos esperados del precio y que cualquier otro error se vea y no quede escondido bajo un 0.

Mis primeras pruebas no habrían detectado el error del diccionario, así que agregué una que llama dos veces a la función y comprueba que la segunda no arrastra datos de la primera. Comprobé que falla con el código original y pasa con el corregido.

Con más tiempo agregaría pre-commit a la lista de dependencias del proyecto, porque instalarlo a mano no queda registrado para nadie más. No lo hice dentro de mi entrega porque el pull request solo puede tocar mi carpeta. Aprendí que un entorno reproducible depende de que todo quede escrito, y no de lo que uno instala a mano. 


