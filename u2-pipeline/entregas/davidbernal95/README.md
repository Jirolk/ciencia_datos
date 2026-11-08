# Entrega U2 - Pipeline de publicaciones

API pública: https://jsonplaceholder.typicode.com/posts

Desde la raíz del repositorio, dentro del Codespace o Dev Container:

```bash
uv sync --frozen
source .venv/bin/activate
uv pip install -r u2-pipeline/entregas/davidbernal95/requirements.txt
python u2-pipeline/entregas/davidbernal95/comprobar_entrega.py
```

El último comando comprueba estilo, formato y pruebas; consulta la API real,
genera `data.duckdb` y registra las evidencias en `evidencias.json`.
Se necesita acceso a internet para instalar dependencias y consultar la API.
Las pruebas utilizan respuestas simuladas y no consultan internet.

También se pueden ejecutar los controles por separado:

```bash
ruff check u2-pipeline/entregas/davidbernal95
ruff format --check u2-pipeline/entregas/davidbernal95
pytest u2-pipeline/entregas/davidbernal95 -q
python u2-pipeline/entregas/davidbernal95/pipeline.py
python u2-pipeline/entregas/davidbernal95/verificar_datos.py
```

La base se guarda junto a los scripts. La tabla es `jsonplaceholder.posts`.
La carga validada obtuvo 100 publicaciones: diez por cada uno de diez usuarios.
Cada nueva ejecución reemplaza la colección anterior. Una respuesta vacía,
inválida o un error HTTP interrumpe la extracción.

`evidencias.json` conserva los resultados de una ejecución; volver a ejecutar
el comprobador actualiza ese archivo. La base y el estado temporal de dlt
están excluidos de Git y se vuelven a generar con los comandos anteriores.
