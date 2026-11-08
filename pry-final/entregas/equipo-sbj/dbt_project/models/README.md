# Modelos dbt - Minimercado

## Convenciones
* `stg_*` → staging, views en schema `staging`
* `int_*` → intermediate, views en schema `intermediate`
* `mart_*` → marts, tables en schema `marts`

## Fuentes
`raw` → tablas cargadas por dlt desde CSV sintéticos.

## Dependencias
Marts dependen de Intermediate, que depende de Staging.

## Tests
Ejecutar `dbt test` para validar schema.yml y tests singulares.
