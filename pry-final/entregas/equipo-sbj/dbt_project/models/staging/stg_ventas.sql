with base as (

    select
        cast(id as integer)                     as venta_id,
        cast(fecha as date)                     as fecha_venta,
        cast(producto_id as integer)            as producto_id,
        cast(cantidad as integer)               as cantidad,
        cast(precio_unitario as decimal(12, 2)) as precio_unitario,
        cast(descuento as decimal(5, 4))        as descuento,   -- proporción: 0.10 = 10 %
        cast(vendedor_id as integer)            as vendedor_id
    from {{ source('raw', 'ventas') }}

),

importes as (

    select
        *,
        cast(round(cantidad * precio_unitario, 2) as decimal(14, 2)) as importe_bruto
    from base

)

select
    *,
    cast(round(importe_bruto * descuento, 2) as decimal(14, 2))                  as importe_descuento,
    cast(importe_bruto - round(importe_bruto * descuento, 2) as decimal(14, 2))  as importe_neto
from importes
