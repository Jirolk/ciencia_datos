# Informe de unidad

Informe técnico acotado para el cierre de cada unidad

---

## Unidad: U2: Mi primer pipeline de datos con dlt y DuckDB

**Nombre:** David Helmut Reese Molinas

**Usuario GitHub:** 3241844facet

**Fecha:** 25 de Octubre de 2026

**Tag de cierre:** `u2-completa`

---

### Qué se hizo

En esta segunda unidad construí un pipeline de extracción y carga (EL) automatizado en Python utilizando la librería
`dlt` para consumir datos paginados desde la API pública PokeAPI (`https://pokeapi.co/api/v2/pokemon`), enriquecerlos
con metadatos detallados de cada entidad (tipos, habilidades y movimientos) e insertarlos en el motor analítico `DuckDB`.

#### Entorno
Trabajé sobre el entorno configurado en el Dev Container del repositorio. Verifiqué la instalación de las
dependencias `dlt`, `duckdb` y `requests`, asegurando que los comandos de prueba y linter ejecutaran correctamente.

#### Flujo de Git
Creé la rama de trabajo `u2/3241844facet` e introduje los archivos dentro de la carpeta
`u2-pipeline/entregas/3241844facet/`. Desde allí todos los commits del proyecto fueron enviados según los avances 
logrados, siendo estos lo suficientemente explicativos para cumplir las buenas prácticas de desarrollo y abrí el 
Pull Request correspondiente en mi fork hacia la rama `main` del proyecto principal.

---

### Una decisión de diseño, explicada

Elegí estructurar un pipeline en el recurso `pokemon` que serializa los atributos anidados mediante `json.dumps()` y
acota el consumo a 5 páginas con un límite de 40 registros por página (200 registros en total).

Por un lado, al enviar listas nativas, la normalización de `dlt` intentaba crear tablas relacionales secundarias
(`pokemon__tipos`). Decidí rechazar la creación de tablas secundarias y mantener los atributos serializados en un solo
campo para evitar JOINs complejos en DuckDB, preservando una estructura plana y eficiente en una única tabla.

Por otro lado, limitar la extracción a 10 páginas evita realizar más de 1.300 peticiones individuales al catálogo
completo, acelerando la ejecución local a pocos segundos y previniendo el bloqueo de IP por *rate limiting*. Esto
demuestra la paginación de forma óptima sin sobrecargar el servidor remoto.

Adicionalmente, implementé la eliminación previa de `data.duckdb` en `main()` para garantizar la reconstrucción limpia
e incorporé pausas de *cooldown* con `time.sleep` entre solicitudes.

---

### Un problema que apareció

Durante la ejecución y pruebas del pipeline se identificaron dos problemas principales.

En primer lugar, realizar múltiples peticiones consecutivas por cada Pokémon a la API pública podía causar un bloqueo
temporal o error HTTP 429 por saturación de tráfico. Lo solucioné implementando pausas cortas de 0.1s por detalle y
0.5s entre páginas, asegurando un consumo eficiente y respetuoso del servidor.

En segundo lugar, la integración de metadatos enriquecidos requirió adaptar las pruebas unitarias en Pytest. Al
hacer peticiones anidadas, se implementó un mockeo multinivel con `side_effect` en `requests.get` para simular tanto
la lista paginada como los JSONs individuales. Asimismo, se gestionó la abstracción de `dlt`, que aplana los
generadores con listas y envuelve las fallas de red dentro de su excepción interna `ResourceExtractionError`.

Lo resolví manteniendo una suite de 6 pruebas unitarias que verifican la serialización JSON de atributos, la
paginación múltiple, el manejo de respuestas vacías, errores de red HTTP 500 y las pausas con `mock_sleep`.

---

### Reflexión y ayudas externas

#### Reflexión
Trabajar con `dlt` y `DuckDB` simplifica drásticamente la construcción de pipelines de datos. `dlt` elimina la
necesidad de escribir código repetitivo para el manejo de esquemas o conectores, mientras que `DuckDB` ofrece una
persistencia local sin requerir la administración de servidores de bases de datos pesados.

#### Ayudas externas
Para completar la tarea utilicé la documentación oficial de dlt sobre recursos paginados y excepciones
(https://dlthub.com/docs/) y la guía oficial de Pytest para el uso de mocks (https://docs.pytest.org/en/stable/).

Asimismo, utilicé la asistencia interactiva de Gemini para depurar la creación no deseada de tablas secundarias por
normalización en `dlt`, evaluar el impacto del límite de páginas y redactar el informe técnico.

---

### Qué harías distinto con más tiempo

Con más tiempo, implementaría carga incremental (`incremental`) basada en marcas de tiempo para evitar re-descargar la
totalidad de los registros en cada corrida, y agregaría validaciones de calidad de datos con contratos de datos de
`dlt`.