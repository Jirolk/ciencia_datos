-- Falla si el historial de movimientos no tiene tantas filas como la tabla cruda de movimientos.
select
    (select count(*) from {{ ref('int_movimientos_stock') }}) as filas_dbt,
    (select count(*) from {{ source('raw_minimercado', 'movimientos_stock') }}) as filas_origen
where filas_dbt <> filas_origen