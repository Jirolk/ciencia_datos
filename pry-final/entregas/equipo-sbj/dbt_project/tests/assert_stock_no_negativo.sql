-- Falla si en algún momento el stock acumulado de un producto fue negativo.
select producto_id, movimiento_id, stock_acumulado
from {{ ref('int_movimientos_stock') }}
where stock_acumulado < 0
