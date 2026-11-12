with limites as (
    select min(fecha) as inicio, max(fecha) as fin
    from {{ ref('stg_movimientos_stock') }}
)
select cast(dia as date) as fecha
from limites,
    lateral generate_series(inicio, fin, interval '1 day') as calendario(dia)
