select
    cast(id as bigint) as compra_id,
    cast(fecha as date) as fecha,
    cast(producto_id as bigint) as producto_id,
    cast(cantidad as integer) as cantidad,
    cast(costo_unitario as decimal(18, 2)) as costo_unitario,
    trim(proveedor) as proveedor
from {{ source('minimercado', 'compras') }}
