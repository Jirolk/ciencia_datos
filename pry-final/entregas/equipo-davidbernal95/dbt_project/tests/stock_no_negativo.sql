select *
from {{ ref('int_movimientos_stock') }}
where saldo_stock < 0
