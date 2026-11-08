select
    cast(id as integer)         as vendedor_id,
    trim(nombre)                as nombre_vendedor,
    lower(trim(sucursal))       as sucursal,
    cast(fecha_alta as date)    as fecha_alta
from {{ source('raw', 'vendedores') }}
