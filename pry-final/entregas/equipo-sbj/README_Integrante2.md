# Integrante 2 - Analytics Engineering

## Responsabilidad
Diseño del proyecto dbt en tres capas + configuración de pruebas de calidad en SQL.

## Estructura dbt

```
dbt_project/
├── dbt_project.yml
├── profiles.yml
├── macros/
│   └── generate_schema_name.sql
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── schema.yml
│   │   ├── stg_productos.sql
│   │   ├── stg_vendedores.sql
│   │   ├── stg_compras.sql
│   │   ├── stg_ventas.sql
│   │   └── stg_movimientos_stock.sql
│   ├── intermediate/
│   │   ├── schema.yml
│   │   ├── int_ventas_enriquecidas.sql
│   │   └── int_movimientos_stock.sql
│   └── marts/
│       ├── schema.yml
│       ├── mart_ventas_diarias.sql
│       ├── mart_rentabilidad_productos.sql
│       ├── mart_rotacion_inventario.sql
│       ├── mart_desempeno_vendedores.sql
│       └── mart_clasificacion_abc.sql
└── tests/
    ├── assert_importes_positivos.sql
    ├── assert_stock_no_negativo.sql
    ├── assert_venta_posterior_a_alta_vendedor.sql
    ├── assert_marts_concilian_con_ventas.sql
    └── assert_abc_participacion_100.sql
```

## Capas

### Staging
Limpieza, casteo y normalización desde `raw`:
* `stg_productos` → producto_id, nombre_producto, categoria, costo_unitario, precio_venta
* `stg_vendedores` → vendedor_id, nombre_vendedor, fecha_alta
* `stg_compras` → compra_id, producto_id, fecha_compra, cantidad
* `stg_ventas` → venta_id, fecha_venta, producto_id, cantidad, precio_unitario, descuento, vendedor_id, importe_bruto, importe_descuento, importe_neto
* `stg_movimientos_stock` → movimiento_id, producto_id, tipo, motivo

Tests en `schema.yml`: `not_null`, `unique`, `relationships`, `accepted_values`.

### Intermediate
Integración y lógica previa:
* `int_ventas_enriquecidas` → ventas + producto + vendedor con costo y ganancia bruta
* `int_movimientos_stock` → signo de movimiento y stock acumulado con función de ventana

### Marts
Modelos de negocio:
* `mart_ventas_diarias` → resumen diario con calendario completo, ingreso_neto, unidades_vendidas, ganancia_bruta
* `mart_rentabilidad_productos` → ganancia bruta por producto
* `mart_rotacion_inventario` → rotación, días de stock, punto de reposición con vars `dias_reposicion`, `dias_seguridad`, `ventana_dias`
* `mart_desempeno_vendedores` → métricas acumuladas por vendedor
* `mart_clasificacion_abc` → clasificación Pareto A/B/C con acumulado previo

## Calidad de datos

**schema.yml** por capa con:
* `not_null` en claves y métricas críticas
* `unique` en claves primarias
* `relationships` hacia staging
* `accepted_values` para tipo y motivo y clasificación ABC

**Pruebas singulares en `tests/`**
* importes positivos
* stock nunca negativo
* venta posterior al alta del vendedor
* conciliación ingresos raw ↔ marts
* participación ABC = 100%

## Comandos de reproducción

```bash
# Configurar variable de DuckDB
$env:DUCKDB_PATH = "D:\ruta\al\data.duckdb"

# Instalar dependencias
pip install dbt-core dbt-duckdb

# Validar proyecto
dbt --project-dir dbt_project debug

# Compilar
dbt --project-dir dbt_project compile

# Ejecutar con tests
dbt --project-dir dbt_project build --select minimercado

# Documentación
dbt --project-dir dbt_project docs generate
dbt --project-dir dbt_project docs serve
```

## Decisiones de modelado

* Staging materializado como view para reflejar raw en tiempo real.
* Intermediate como view para reutilización.
* Marts como table para consultas analíticas rápidas.
* Calendario completo en `mart_ventas_diarias` para estadísticas no sesgadas.
* Ganancia bruta = importe_neto - cantidad * costo de catálogo.
* Punto de reposición = venta_diaria_30d * (dias_reposicion + dias_seguridad).
* Clasificación ABC con acumulado previo para umbrales 80% / 95%.

## Variables dbt

Definidas en `dbt_project.yml`:
* `dias_reposicion: 7`
* `dias_seguridad: 3`
* `ventana_dias: 30`

## Próximos pasos Integrante 3
Orquestar con Dagster y agregar pruebas pytest.
