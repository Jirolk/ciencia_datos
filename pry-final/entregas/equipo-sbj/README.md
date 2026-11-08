# Equipo-sbj - Pipeline analítico de un minimercado

Pipeline de datos reproducible de extremo a extremo (*Modern Data Stack*):
Python · `dlt` · DuckDB · `dbt` · Dagster · `pytest`.

## Estructura de la entrega

```text
pry-final/entregas/equipo-sbj/
├── pyproject.toml            # dependencias y config de pytest
├── README.md                 # este archivo
├── generar_datos.py          # Integrante 1: datos sintéticos (semilla 42)
├── pipeline.py               # Integrante 1: ingesta idempotente con dlt → DuckDB
├── data/                     # CSV sintéticos generados (5 tablas)
├── dbt_project/              # Integrante 2: staging / intermediate / marts + pruebas SQL
├── orchestration/            # Integrante 3: orquestación con Dagster
│   └── definitions.py        #   4 assets encadenados + job pipeline_completo
├── analisis.py               # Integrante 3: consultas finales + reporte de calidad
├── consultas_analisis.sql    # Integrante 3: consultas SQL de negocio
├── test_pipeline.py          # Integrante 3: suite de pruebas pytest
└── informe.md                # Integrante 3: informe técnico (700-1000 palabras)
```

## Requisitos

- Python >= 3.10
- Las dependencias (`dlt`, `duckdb`, `dbt-core`, `dbt-duckdb`, `dagster`, `pytest`)
  se instalan con `pip install -e ".[dev]"` (ver paso 1).

## Reproducción desde cero

```bash
# 0. Entrar a la carpeta de la entrega
cd pry-final/entregas/equipo-sbj

# 1. Crear y activar el entorno virtual, instalar dependencias
python -m venv .venv
# Linux/macOS:  source .venv/bin/activate
# Windows:      .venv\Scripts\activate
pip install -e ".[dev]"

# 2. Generar los datos sintéticos (semilla fija 42) -> data/*.csv
python generar_datos.py

# 3. Ingesta idempotente con dlt -> data.duckdb (esquema raw).
#    Reejecutar NO duplica filas (write_disposition = merge).
python pipeline.py

# 4. Transformación y calidad con dbt: staging -> intermediate -> marts
#    (incluye las pruebas de integridad y las 5 pruebas singulares)
dbt build --project-dir dbt_project --profiles-dir dbt_project

# 5. Análisis final: consultas de negocio y reporte de calidad
python analisis.py              # imprime las consultas de consultas_analisis.sql
python analisis.py --calidad    # además valida la salida -> reportes/reporte_calidad.json

# 6. Orquestación con Dagster (interfaz web en http://localhost:3000)
dagster dev -f orchestration/definitions.py
# o todo el flujo por línea de comandos:
dagster asset materialize --select "*" -f orchestration/definitions.py

# 7. Pruebas automatizadas
pytest test_pipeline.py
```

> **Variable opcional:** `DUCKDB_PATH` cambia la ubicación de `data.duckdb`
> (por defecto `./data.duckdb` en esta carpeta). La usan dbt, Dagster y los tests.

## Flujo del pipeline

```text
generar_datos.py → data/*.csv → pipeline.py (dlt) → data.duckdb [raw]
      → dbt staging → dbt intermediate → dbt marts
      → analisis.py (consultas + reporte de calidad)
Dagster orquesta los 4 assets: generar_datos → ingesta_dlt → dbt → reporte_calidad
```

## Roles

| Integrante | Responsabilidad |
| :--- | :--- |
| **Integrante 1 - Ingeniería de Datos** | `generar_datos.py`, `pipeline.py`, `data/*.csv` |
| **Integrante 2 - Analytics Engineering** | `dbt_project/` (staging, intermediate, marts, pruebas SQL) |
| **Integrante 3 - Orquestación & QA** | `orchestration/definitions.py`, `test_pipeline.py`, `analisis.py`, `consultas_analisis.sql`, `informe.md`, `README.md` |

## Integrantes

- Integrante 1: Ingeniería de Datos
- Integrante 2: Analytics Engineering
- Integrante 3: Orquestación & QA
