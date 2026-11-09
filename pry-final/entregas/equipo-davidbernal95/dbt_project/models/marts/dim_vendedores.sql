-- Una fila por vendedor, sin historial de cambios en esta simulación.
select vendedor_id, vendedor, sucursal, fecha_alta
from {{ ref('stg_vendedores') }}
