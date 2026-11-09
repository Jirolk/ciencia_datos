select
    cast(id as bigint) as movimiento_id,
    cast(fecha as date) as fecha,
    cast(producto_id as bigint) as producto_id,
    trim(lower(tipo)) as tipo,
    cast(referencia_id as bigint) as referencia_id,
    cast(cantidad as integer) as cantidad
from {{ source('minimercado', 'movimientos_stock') }}
