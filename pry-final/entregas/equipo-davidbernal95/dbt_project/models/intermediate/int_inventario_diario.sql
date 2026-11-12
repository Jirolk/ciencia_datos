with movimientos_por_dia as (
    select
        producto_id,
        fecha,
        sum(unidades_netas) as unidades_netas,
        sum(case when tipo = 'salida' then -unidades_netas else 0 end) as unidades_vendidas
    from {{ ref('int_movimientos_stock') }}
    group by producto_id, fecha
)
select
    p.producto_id,
    c.fecha,
    coalesce(m.unidades_vendidas, 0) as unidades_vendidas,
    sum(coalesce(m.unidades_netas, 0)) over (
        partition by p.producto_id order by c.fecha
        rows between unbounded preceding and current row
    ) as stock_cierre
from {{ ref('stg_productos') }} p
cross join {{ ref('int_calendario') }} c
left join movimientos_por_dia m
    on p.producto_id = m.producto_id and c.fecha = m.fecha
