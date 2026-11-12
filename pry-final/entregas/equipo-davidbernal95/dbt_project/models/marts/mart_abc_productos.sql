with acumulado as (
    select
        producto_id,
        producto,
        unidades_vendidas,
        facturacion_neta,
        sum(unidades_vendidas) over () as total_unidades,
        sum(unidades_vendidas) over (
            order by unidades_vendidas desc, producto_id
            rows between unbounded preceding and current row
        ) as unidades_acumuladas
    from {{ ref('mart_rentabilidad_productos') }}
)
select
    producto_id,
    producto,
    unidades_vendidas,
    facturacion_neta,
    round(100.0 * unidades_acumuladas / nullif(total_unidades, 0), 2) as acumulado_pct,
    case
        when unidades_vendidas = 0 then 'C'
        when 100 * (unidades_acumuladas - unidades_vendidas) < 80 * total_unidades then 'A'
        when 100 * (unidades_acumuladas - unidades_vendidas) < 95 * total_unidades then 'B'
        else 'C'
    end as clase_abc
from acumulado
