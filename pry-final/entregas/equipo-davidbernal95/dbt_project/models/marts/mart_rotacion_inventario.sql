with resumen as (
    select
        producto_id,
        count(*) as dias_observados,
        arg_max(stock_cierre, fecha) as stock_actual,
        avg(stock_cierre) as stock_promedio,
        sum(unidades_vendidas) as unidades_vendidas,
        avg(unidades_vendidas) as demanda_diaria_media,
        count(*) filter (where stock_cierre > 0) as dias_con_stock
    from {{ ref('int_inventario_diario') }}
    group by producto_id
),
metricas as (
    select
        r.*,
        p.producto,
        ceil(7 * demanda_diaria_media)::integer as punto_reposicion,
        round(stock_actual / nullif(demanda_diaria_media, 0), 2) as dias_cobertura,
        round(unidades_vendidas / nullif(stock_promedio, 0), 2) as rotacion_unidades
    from resumen r
    join {{ ref('dim_productos') }} p using (producto_id)
)
select *, stock_actual < punto_reposicion as bajo_reposicion
from metricas
