# Tarea Integradora Final: Pipeline Analítico de un Minimercado

> **Modalidad:** Equipo (3 integrantes)  
> **Stack Tecnológico:** Python, `dlt`, DuckDB, `dbt`, Dagster, `pytest`, Git/GitHub  

---

## 1. Objetivo General

Construir un pipeline de datos reproducible y de extremo a extremo que simule la operación de un minimercado mediante datos sintéticos. El proyecto abarca desde la generación e ingesta de datos hasta la transformación dimensional, control de calidad, análisis analítico y orquestación dentro de una arquitectura moderna de datos (*Modern Data Stack*).

---

## 2. Distribución Recomendada de Roles

Para completar el trabajo de manera eficiente en una semana, se sugiere distribuir las responsabilidades entre los tres integrantes:

| Rol / Integrante | Responsabilidades Principales |
| :--- | :--- |
| **Integrante 1: Ingeniería de Datos** | Generación de datos sintéticos (`generar_datos.py`) e ingesta idempotente con `dlt` hacia DuckDB. |
| **Integrante 2: Analytics Engineering** | Diseño del proyecto `dbt` (Staging, Intermediate, Marts) y configuración de pruebas de calidad en SQL. |
| **Integrante 3: Orquestación & QA** | Implementación del flujo en Dagster, creación de pruebas con `pytest` y redacción del informe técnico. |

---

## 3. Requerimientos

### Generación de Datos Sintéticos
Desarrollar un módulo en Python (`generar_datos.py`) que produzca un conjunto de datos coherente y reproducible (usando una semilla fija `seed`).
* **Cobertemporal:** Mínimo 90 días de actividad.
* **Entidades mínimas:**
  * `Productos`: 20 registros (id, nombre, categoría, costo_unitario, precio_venta, stock_inicial).
  * `Vendedores`: 5 registros (id, nombre, sucursal, fecha_alta).
  * `Compras`: Mínimo 100 registros (id, fecha, producto_id, cantidad, costo_unitario, proveedor).
  * `Ventas`: Mínimo 500 registros (id, fecha, producto_id, cantidad, precio_unitario, descuento, vendedor_id).
  * `Movimientos_Stock`: Registro de entradas y salidas de almacén.
* **Consistencia:** Mantener claves referenciales, importes positivos y variaciones de demanda por día/producto.
* **Entregable:** Archivos CSV o JSON en la carpeta `data/`.

---

### Ingesta y Persistencia con `dlt` y DuckDB
Implementar un pipeline de ingesta (`pipeline.py`) utilizando la librería `dlt`.
* **Origen:** Archivos generados previamente.
* **Destino:** Base de datos relacional local `data.duckdb`.
* **Idempotencia:** Asegurar que la reejecución del script no cree registros duplicados en la base de datos.
* **Entregable:** Script `pipeline.py` y configuración de recursos en `dlt`.

---

### Transformación y Modelado con `dbt`
Construir un proyecto de `dbt` organizado en tres capas principales:
1. **Staging (`models/staging/`):** Limpieza, casteo de tipos de datos y normalización de nombres (`stg_ventas`, `stg_compras`, `stg_productos`, `stg_vendedores`).
2. **Intermediate (`models/intermediate/`):** Integración de tablas y lógica previa de inventarios (`int_movimientos_stock`).
3. **Marts (`models/marts/`):**
   * `mart_ventas_diarias`: Resumen diario por fecha.
   * `mart_rentabilidad_productos`: Cálculo de ganancia bruta por producto considerando costos.
   * `mart_rotacion_inventario`: Días de stock disponibles por producto.
   * `mart_desempeno_vendedores`: Métricas de venta acumulada por vendedor.
   * *Extra:* Clasificación ABC de productos basada en volumen de ventas.
* **Calidad de Datos:** Definir `schema.yml` con pruebas de integridad (`not_null`, `unique`, `relationships`).

---

### Análisis Estadístico e Indicadores
Construir consultas SQL finales para responder a las siguientes preguntas del negocio:
1. **Análisis Descriptivo:** Facturación total, unidades vendidas, promedio, mediana y desviación estándar de ventas diarias.
2. **Inventario:** Rotación de inventario y detección de productos por debajo del punto de reposición.
3. **Comercial:** Identificación del top de vendedores, distribución ABC de ventas.

---

### Orquestación con Dagster
Crear una definición en Dagster (`orchestration/definitions.py`) que exponga los pasos del pipeline como *Assets*:
1. `generar_datos_asset`: Ejecuta el script de datos.
2. `ingesta_dlt_asset`: Ejecuta la ingesta a DuckDB.
3. `dbt_transformations_asset`: Corre los modelos y pruebas de `dbt`.
4. `reporte_calidad_asset`: Valida la salida final.
* Debe ser posible ejecutar el flujo completo desde la interfaz o línea de comandos de Dagster.

---

### Pruebas Automatizadas
Implementar un suite de pruebas con `pytest` (`test_pipeline.py`) que incluya:
* Verificación de la reproducibilidad en la generación de datos.
* Comprobación del esquema en DuckDB tras la ingesta de `dlt`.
* Prueba de integración de punta a punta (End-to-End).

---

### Informe Técnico y Documentación
Redactar un documento en formato Markdown (`informe.md`) de entre 700 y 1.000 palabras que incluya:
* Explicación del diagrama de arquitectura.
* Principales decisiones de modelado analítico y calidad de datos.
* Resumen de hallazgos estadísticos y comerciales obtenidos.
* Limitaciones del conjunto de datos y oportunidades de mejora.

---

## 4. Estructura de Entregables del Repositorio

Cada equipo entregará su trabajo dentro de una carpeta identificada con sus usuarios:

```text
pry-final/
└── entregas/
    └── equipo-<nombre_equipo>/
        ├── pyproject.toml
        ├── README.md
        ├── generar_datos.py
        ├── pipeline.py
        ├── test_pipeline.py
        ├── data/                  # Archivos sintéticos
        ├── dbt_project/           # Proyecto dbt completo
        │   ├── dbt_project.yml
        │   ├── models/
        │   └── tests/
        ├── orchestration/         # Definiciones de Dagster
        │   └── definitions.py
        └── informe.md             # Informe técnico final
```

---

## 5. Criterios de Evaluación

| Dimensión | Ponderación | Descripción |
| :--- | :---: | :--- |
| **Generación y Consistencia** | 10% | Reproducibilidad con semilla y coherencia de los datos sintéticos. |
| **Ingesta (`dlt` + DuckDB)** | 15% | Carga correcta, limpia e idempotente en DuckDB. |
| **Modelado (`dbt`)** | 20% | Estructura modular (Staging/Marts) y presencia de pruebas de calidad. |
| **Análisis y Métricas** | 25% | Exactitud en los cálculos de rentabilidad, clasificación ABC y estadísticas. |
| **Orquestación (`Dagster`)** | 15% | Flujo automatizado sin fallos con dependencias bien definidas. |
| **Calidad, Git y Documentación** | 15% | Commits claros por integrante, pruebas `pytest` e informe consolidado. |
| **Total** | **100%** | |

---

## 6. Reglas de Entrega

1. **Flujo Git:** Trabajar en una rama compartida `pyt/equipo-<nombre>`.
2. **Historial de Trabajo:** Se requiere un mínimo de **9 commits en total** (al menos 3 commits significativos por cada integrante).
3. **Pull Request:** Abrir el PR hacia la rama `main` del repositorio del curso modificando **únicamente** la carpeta asignada al equipo.
4. **Instrucciones:** El archivo `README.md` de la carpeta debe incluir los comandos exactos para reproducir todo el flujo desde cero.
