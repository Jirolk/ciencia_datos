select
    cast(id as integer) as venta_id,
    cast(fecha as date) as fecha_venta,
    cast(producto_id as integer) as producto_id,
    cast(cantidad as integer) as cantidad,
    cast(precio_unitario as decimal(12, 2)) as precio_unitario,
    cast(descuento as decimal(4, 2)) as descuento,
    cast(vendedor_id as integer) as vendedor_id
from {{ source('raw_minimercado', 'ventas') }}