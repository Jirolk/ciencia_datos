select
    cast(id as bigint) as producto_id,
    trim(nombre) as producto,
    trim(categoria) as categoria,
    cast(costo_unitario as decimal(18, 2)) as costo_inicial,
    cast(precio_venta as decimal(18, 2)) as precio_lista,
    cast(stock_inicial as integer) as stock_inicial
from {{ source('minimercado', 'productos') }}
