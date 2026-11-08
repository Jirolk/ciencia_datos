# Checklist Integrante 2 - Analytics Engineering

## Requisitos del enunciado

### Staging
- [x] `stg_ventas` con limpieza, casteo y normalización
- [x] `stg_compras` con limpieza, casteo y normalización
- [x] `stg_productos` con limpieza, casteo y normalización
- [x] `stg_vendedores` con limpieza, casteo y normalización
- [x] Nombres normalizados: producto_id, fecha_venta, etc.

### Intermediate
- [x] `int_movimientos_stock` con integración e inventario
- [x] `int_ventas_enriquecidas` para unión producto/vendedor

### Marts
- [x] `mart_ventas_diarias` → resumen diario
- [x] `mart_rentabilidad_productos` → ganancia bruta por producto
- [x] `mart_rotacion_inventario` → días de stock disponibles
- [x] `mart_desempeno_vendedores` → métricas por vendedor
- [x] Extra `mart_clasificacion_abc` → clasificación ABC

### Calidad de datos
- [x] `schema.yml` en staging con `not_null`, `unique`, `relationships`
- [x] `schema.yml` en intermediate con `not_null`, `unique`, `relationships`
- [x] `schema.yml` en marts con `not_null`, `unique`, `relationships`
- [x] Pruebas singulares en `tests/`:
  - [x] importes positivos
  - [x] stock no negativo
  - [x] venta posterior a alta vendedor
  - [x] conciliación marts vs ventas
  - [x] participación ABC = 100%

### Configuración
- [x] `dbt_project.yml` con 3 capas y esquemas staging/intermediate/marts
- [x] `profiles.yml` apuntando a DuckDB
- [x] Vars de negocio: dias_reposicion, dias_seguridad, ventana_dias
- [x] `sources.yml` definiendo raw

## Estado actual
Todos los archivos requeridos existen y están copiados desde el repositorio de trabajo.

## Próximas validaciones
1. Ejecutar `dbt compile` para validar SQL
2. Ejecutar `dbt build` con base de datos del Integrante 1
3. Generar `dbt docs`
4. Revisar logs de tests para asegurar 0 fallos

## Entregables Integrante 2
- dbt_project completo con 3 capas
- schema.yml con pruebas de integridad
- tests singulares en SQL
- README_Integrante2.md con decisiones de modelado
