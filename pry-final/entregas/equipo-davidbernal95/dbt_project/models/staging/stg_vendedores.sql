select
    cast(id as bigint) as vendedor_id,
    trim(nombre) as vendedor,
    trim(sucursal) as sucursal,
    cast(fecha_alta as date) as fecha_alta
from {{ source('minimercado', 'vendedores') }}
