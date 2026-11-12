with esperado as (
    select 'entrada' as tipo, compra_id as referencia_id, producto_id, fecha, cantidad
    from {{ ref('stg_compras') }}
    union all
    select 'salida' as tipo, venta_id as referencia_id, producto_id, fecha, cantidad
    from {{ ref('stg_ventas') }}
),
observado as (
    select tipo, referencia_id, producto_id, fecha, cantidad
    from {{ ref('stg_movimientos_stock') }}
),
faltantes as (
    select * from esperado except all select * from observado
),
sobrantes as (
    select * from observado except all select * from esperado
)
select * from faltantes
union all
select * from sobrantes
