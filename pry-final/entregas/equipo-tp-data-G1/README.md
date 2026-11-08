# Equipo tp-data-G1 · Pipeline analítico de un minimercado

Pipeline reproducible de punta a punta: datos sintéticos, ingesta con **dlt** a **DuckDB**,
modelado con **dbt**, orquestación con **Dagster** y pruebas con **pytest**.

```text
generar_datos.py ──► data/*.csv ──► pipeline.py (dlt) ──► data.duckdb
                                                          ├─ raw_minimercado  (datos crudos)
                                                          └─ analytics        (dbt: staging, intermediate, marts)
```

## Integrantes

| Integrante | Usuario | Rol | Archivos |
|---|---|---|---|
| REBEKA ROJAS | rebekakrauer | Ingeniería de datos | `generar_datos.py`, `pipeline.py`, `data/` |
| VICTOR ROBLES | VictoRobles | Analytics engineering | `dbt_project/`, `consultas.py` |
| LOURDES MOLINAS | 5389410-lang | Orquestación y QA | `orchestration/`, `test_pipeline.py`, `informe.md`, `README.md` |

## Reproducir todo desde cero

### 1. Entorno

**Opción A: GitHub Codespaces** (recomendada; el repo del curso ya trae todo instalado).
En el fork, elegir la rama `pyt/equipo-tp-data-G1`, luego **Code → Codespaces → Create codespace**.
En la terminal:

```bash
source .venv/bin/activate
cd pry-final/entregas/equipo-tp-data-G1
```

**Opción B: computadora propia** (Python 3.11 o superior), desde esta carpeta:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

### 2. Flujo completo con Dagster (un solo comando)

Desde esta carpeta:

```bash
mkdir -p .dagster
export DAGSTER_HOME=$(pwd)/.dagster
dagster job execute -f orchestration/definitions.py -j pipeline_completo_job
```

Termina con `RUN_SUCCESS` y deja el resultado de los controles en `reporte_calidad.json`.

Con la interfaz web:

```bash
dagster dev -f orchestration/definitions.py
```

Abrir <http://localhost:3000> (en Codespaces, el botón **Open in Browser** que aparece abajo a la
derecha), ir a **Assets** y presionar **Materialize all**. El schedule `carga_nocturna`
(todos los días a las 02:00) queda apagado; se activa en la pestaña **Automation**.

### 3. Flujo paso a paso (sin Dagster)

```bash
python generar_datos.py              # 5 CSV en data/ (semilla 42)
python pipeline.py                   # carga a data.duckdb, esquema raw_minimercado
cd dbt_project
dbt build --profiles-dir .           # 11 modelos + 48 pruebas (PASS=59)
cd ..
python consultas.py                  # consultas de negocio de dbt_project/analyses/
```

### 4. Pruebas y estilo

```bash
pytest -v                            # 7 pruebas
```

Desde la raíz del repositorio, con la configuración de ruff del curso:

```bash
ruff check pry-final/entregas/equipo-tp-data-G1
ruff format --check pry-final/entregas/equipo-tp-data-G1
```

## Estructura

```text
├── generar_datos.py           datos sintéticos con semilla fija (120 días)
├── pipeline.py                ingesta con dlt (merge por id: no duplica filas)
├── data/                      CSV generados
├── dbt_project/
│   ├── models/staging/        stg_productos, stg_vendedores, stg_compras, stg_ventas
│   ├── models/intermediate/   int_movimientos_stock, int_ventas_detalle
│   ├── models/marts/          ventas diarias, rentabilidad, rotación, vendedores, ABC
│   ├── tests/                 pruebas de reglas de negocio
│   └── analyses/              consultas de análisis descriptivo, inventario y comercial
├── consultas.py               ejecuta las consultas de analyses/
├── orchestration/
│   └── definitions.py         4 assets de Dagster, job y schedule
├── test_pipeline.py           pruebas de reproducibilidad, esquema y punta a punta
└── informe.md                 informe técnico
```

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `Could not set lock on file` | Otro proceso (Dagster, dbt) tiene `data.duckdb` abierto | Cerrar ese proceso y volver a ejecutar |
| `dagster: command not found` | El entorno no está activado | `source .venv/bin/activate` desde la raíz del repo |
| dbt no encuentra las tablas | Se ejecutó dbt antes de `pipeline.py`, o fuera de `dbt_project/` | Correr la ingesta y ejecutar dbt desde `dbt_project/` |