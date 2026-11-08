-- Falla si algún movimiento deja el stock de un producto por debajo de cero.
select *
from {{ ref('int_movimientos_stock') }}
where stock_despues < 0