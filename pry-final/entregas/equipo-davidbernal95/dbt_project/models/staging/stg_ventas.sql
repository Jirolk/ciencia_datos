with tipadas as (
    select
        cast(id as bigint) as venta_id,
        cast(fecha as date) as fecha,
        cast(producto_id as bigint) as producto_id,
        cast(vendedor_id as bigint) as vendedor_id,
        cast(cantidad as integer) as cantidad,
        cast(precio_unitario as decimal(18, 2)) as precio_unitario,
        cast(descuento as decimal(8, 4)) as descuento
    from {{ source('minimercado', 'ventas') }}
)
select
    *,
    cast(cantidad * precio_unitario as decimal(18, 2)) as importe_bruto,
    cast(round(cantidad * precio_unitario * (1 - descuento), 2) as decimal(18, 2))
        as importe_neto
from tipadas
