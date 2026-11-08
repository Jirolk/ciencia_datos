select
    cast(id as integer)                                         as compra_id,
    cast(fecha as date)                                         as fecha_compra,
    cast(producto_id as integer)                                as producto_id,
    cast(cantidad as integer)                                   as cantidad,
    cast(costo_unitario as decimal(12, 2))                      as costo_unitario,
    trim(proveedor)                                             as proveedor,
    cast(round(cantidad * costo_unitario, 2) as decimal(14, 2)) as importe_compra
from {{ source('raw', 'compras') }}
