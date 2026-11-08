select
    cast(id as integer)             as movimiento_id,
    cast(fecha as date)             as fecha_movimiento,
    cast(producto_id as integer)    as producto_id,
    lower(trim(tipo))               as tipo,          -- entrada | salida
    cast(cantidad as integer)       as cantidad,
    lower(trim(motivo))             as motivo,        -- stock_inicial | compra | venta | merma
    cast(referencia_id as integer)  as referencia_id  -- id de la compra/venta de origen (nulo si no aplica)
from {{ source('raw', 'movimientos_stock') }}
