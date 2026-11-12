-- Una fila por producto; el identificador del catálogo es la clave natural estable.
select producto_id, producto, categoria, costo_inicial, precio_lista, stock_inicial
from {{ ref('stg_productos') }}
