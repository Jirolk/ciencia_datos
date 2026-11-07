# Pipeline analítico de un minimercado

Entrega individual: Joel Bernal (`davidbernal95`).

El proyecto simula 90 días de compras, ventas e inventario y produce indicadores en
DuckDB. Los nombres de personas y proveedores son ficticios. Los importes están
expresados en guaraníes (PYG).

## Reproducir en Codespaces o Linux

Desde la raíz del repositorio, entrá a la carpeta del proyecto. Si el equipo cambia
de nombre, usá el nombre de carpeta acordado con el docente.

```bash
cd pry-final/entregas/equipo-davidbernal95
python3.12 -m venv .runtime/herramientas
.runtime/herramientas/bin/python -m pip install uv==0.11.8
export PATH="$PWD/.runtime/herramientas/bin:$PATH"
uv sync --locked --python 3.12

mkdir -p .runtime/dagster
cp orchestration/dagster.yaml .runtime/dagster/dagster.yaml
export DAGSTER_HOME="$PWD/.runtime/dagster"
uv run --locked dagster job execute -m orchestration.definitions -j minimercado_job

uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

El entorno del curso puede traer una versión anterior de uv; los primeros comandos
instalan la versión con la que se generó el lockfile sin cambiar el uv global.
La instalación necesita acceso al índice de paquetes. El pipeline trabaja con
archivos locales y no usa credenciales ni APIs externas.

### En Windows (PowerShell)

Con Python 3.12 y uv 0.11.8 disponibles, abrí PowerShell dentro de la carpeta del proyecto:

```powershell
uv sync --locked --python 3.12
New-Item -ItemType Directory -Force .runtime/dagster | Out-Null
Copy-Item orchestration/dagster.yaml .runtime/dagster/dagster.yaml
$env:DAGSTER_HOME = (Resolve-Path .runtime/dagster).Path
uv run --locked dagster job execute -m orchestration.definitions -j minimercado_job
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

### Ejecutar desde Visual Studio Code

Después de instalar las dependencias y preparar `DAGSTER_HOME` con los comandos
anteriores, abrí esta carpeta en Visual Studio Code. En **Ejecutar y depurar**,
elegí **Ejecutar minimercado completo** y presioná **F5**.
La consola de depuración muestra el avance y el resultado de los cuatro pasos.
La configuración usa el Python de `.venv`, tanto en Windows como en Linux.

### Ejecutar desde la interfaz de Dagster

En la misma carpeta y con `DAGSTER_HOME` configurado:

```bash
uv run --locked dagster dev -m orchestration.definitions -p 3000
```

Abrí el puerto 3000 (en Codespaces, desde **Ports**), buscá el job
`minimercado_job` y pulsá **Launch Run**. Los cuatro assets se ejecutan según sus
dependencias. Ejecutá una corrida a la vez por carpeta: DuckDB es un archivo local.

### Ejecutar cada etapa por separado

```bash
uv run --locked python generar_datos.py
uv run --locked python pipeline.py
uv run --locked python transformar.py
uv run --locked python reporte_calidad.py
```

La semilla por defecto es `2026`. Para aislar una corrida alternativa, establecé
`MINIMERCADO_WORKDIR` a otra carpeta antes de ejecutar; así no se reemplazan los CSV
ni la base del proyecto. Los CSV incluidos corresponden a la semilla por defecto.

## Qué queda disponible

- `data/`: cinco CSV de origen. Se regeneran con el mismo contenido para la semilla y período base.
- `data.duckdb`: datos cargados en `raw_minimercado` y modelos en `analitica`.
- `sql/`: consultas de estadística, inventario, vendedores, ABC y rentabilidad.
- `.runtime/reporte_calidad.json`: conciliación y resultados de la corrida local.
- `evidencias/`: resumen y resultados de la ejecución comprobada.
- `informe.md`: arquitectura, decisiones, resultados y límites.
- `referencias_clase.md`: relación entre los apuntes y las decisiones del proyecto.

El modelo de análisis incluye `dim_productos`, `dim_vendedores`, `dim_fecha`,
`fct_ventas` y `fct_compras`. Sobre ese detalle se calculan los cinco marts.
Las consultas 06 y 07 muestran un perfil numérico y los subtotales mensuales.

Las filas de negocio de las cinco tablas se reemplazan con cada carga; el historial
interno de ejecución de dlt puede crecer. La base, el entorno y los artefactos
temporales están excluidos de Git. El archivo `uv.lock` fija las dependencias.

### Cómo leer la cantidad y el promedio de ventas

`lineas_venta` cuenta los registros de venta. `importe_promedio_linea` calcula
el importe neto promedio de esos registros. La simulación no tiene un
`ticket_id` que reúna varias líneas en una compra, por eso este promedio
no se presenta como ticket promedio de una canasta.

El resumen diario incluye fecha, cantidad de líneas, unidades, venta neta,
descuentos e importe promedio por línea. El promedio general se calcula
dividiendo la venta neta total entre todas las líneas, no promediando los
promedios diarios.

Los cuatro assets muestran el linaje de las etapas en Dagster. El detalle de
dependencias entre modelos se define en dbt con `source()` y `ref()`.
Macros personalizadas, contratos de esquema y sensores quedan fuera del
alcance obligatorio de la consigna escrita.

Referencias: [recursos y modos de escritura de dlt](https://dlthub.com/docs/general-usage/resource),
[comando dbt build](https://docs.getdbt.com/reference/commands/build) y
[activos de Dagster](https://docs.dagster.io/guides/build/assets/defining-assets).
