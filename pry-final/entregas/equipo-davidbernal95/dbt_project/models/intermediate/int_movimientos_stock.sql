with eventos as (
    select
        p.producto_id,
        (select min(fecha) from {{ ref('int_calendario') }}) as fecha,
        cast(0 as bigint) as movimiento_id,
        'apertura' as tipo,
        cast(null as bigint) as referencia_id,
        p.stock_inicial as unidades_netas,
        0 as orden
    from {{ ref('stg_productos') }} p

    union all

    select
        producto_id,
        fecha,
        movimiento_id,
        tipo,
        referencia_id,
        case when tipo = 'entrada' then cantidad else -cantidad end as unidades_netas,
        case when tipo = 'entrada' then 1 else 2 end as orden
    from {{ ref('stg_movimientos_stock') }}
)
select
    *,
    sum(unidades_netas) over (
        partition by producto_id order by fecha, orden, movimiento_id
        rows between unbounded preceding and current row
    ) as saldo_stock
from eventos
