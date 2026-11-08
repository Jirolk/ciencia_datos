# Informe U2: Mi primer pipeline de datos con dlt y DuckDB

## Qué construí

Construí un pipeline que toma 100 publicaciones o posts de la API pública JSONPlaceholder, las carga con dlt y las guarda en un archivo local de DuckDB llamado 'data.duckdb'. Después, un segundo script abre esa base, cuenta las filas y filtra los posts del usuario 1. Elegí JSONPlaceholder porque devuelve datos planos y estables, ideales para facilitar mi primer pipeline.

## Decisiones de diseño

Separé la función obtener_posts() del recurso de dlt. Así, en las pruebas puedo reemplazar la llamada a internet por una respuesta falsa y no depender de la red. También usé raise_for_status() y un timeout, para que un error de la API aparezca con claridad en lugar de cargar datos dañados o quedarme esperando.

Usé write_disposition="replace" para que cada ejecución reemplace la tabla, así que correr el pipeline dos veces no duplica filas. Por ejemplo si ubiera usado append, habria 200 posts en la segunda ejecución. Definí la ruta de data.duckdb con Path(__file__).parent, para que el archivo se cree siempre junto al script y tanto el pipeline como verificar_datos.py apunten al mismo lugar. No subí data.duckdb al repositorio porque es un archivo generado que cualquiera puede recrear ejecutando el pipeline y las instrucciones de la tarea no pide su subida.

## El esquema automático de dlt

dlt inspeccionó los datos y creó la tabla jsonplaceholder.posts con seis columnas. Detectó id y userId como números enteros (BIGINT) y title y body como texto (VARCHAR). También normalizó userId a user_id, algo que tuve que recordar al escribir mi consulta SQL. Además agregó dos columnas propias, _dlt_load_id y _dlt_id, que indican en qué carga llegó cada fila y le dan un identificador único. Lo comprobé con: DESCRIBE jsonplaceholder.posts.

Esto fue cómodo, pero tiene un riesgo: no controlo yo el esquema. Si la API cambiara el tipo de un campo, dlt podría crear columnas inesperadas o fallar. Con más tiempo definiría las columnas de forma explícita.

## DuckDB

DuckDB me pareció muy práctico ya que toda la base vive en un solo archivo, sin instalar ni configurar un servidor, y se consulta con SQL normal desde Python. Es ideal para aprender y para proyectos pequeños. Mi duda es qué pasaría con mucha información o con varias personas escribiendo a la vez, porque al ser un archivo local no parece pensado para eso.

## Pruebas y evidencia de ejecución

Escribí tres pruebas con pytest que simulan la API con monkeypatch: una verifica la estructura de los datos, otra una respuesta vacía y otra un error de conexión. Las tres pasan. verificar_datos.py imprime "Total de posts cargados: 100" y los primeros cinco posts del usuario 1.

(curso-analisis-datos) @rebekakrauer ➜ /workspaces/ciencia_datos (u2/rebekakrauer) $ python u2-pipeline/entregas/rebekakrauer/verificar_datos.py
Total de posts cargados: 100
Primeros 5 posts del usuario 1:
  1: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
  2: qui est esse
  3: ea molestias quasi exercitationem repellat qui ipsa sit aut
  4: eum et est occaecati
  5: nesciunt quas odio

## Problemas, mejoras y ayudas externas

Tuve varios tropiezos. uv.lock apareció modificado sin que yo lo tocara y lo descarté con git restore y ruff me pidió corregir el formato y el orden de los imports. Con más tiempo agregaría una prueba que cargue datos en una base temporal y cargaría otros datos adicionales.

Ayudas externas: usé Claude como para entender como debian crearse el pipeline.