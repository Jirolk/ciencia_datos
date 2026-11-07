with compras as (
    select
        producto_id,
        sum(cantidad) as unidades_compradas,
        sum(cantidad * costo_unitario) as costo_compras
    from {{ ref('fct_compras') }}
    group by producto_id
),
ventas as (
    select
        producto_id,
        sum(cantidad) as unidades_vendidas,
        sum(importe_neto) as facturacion_neta
    from {{ ref('fct_ventas') }}
    group by producto_id
),
base as (
    select
        p.producto_id,
        p.producto,
        p.categoria,
        coalesce(v.unidades_vendidas, 0) as unidades_vendidas,
        coalesce(v.facturacion_neta, 0) as facturacion_neta,
        (p.stock_inicial * p.costo_inicial + coalesce(c.costo_compras, 0))
            / nullif(p.stock_inicial + coalesce(c.unidades_compradas, 0), 0)
            as costo_medio_periodo
    from {{ ref('dim_productos') }} p
    left join compras c on p.producto_id = c.producto_id
    left join ventas v on p.producto_id = v.producto_id
),
costeadas as (
    select
        *,
        cast(round(unidades_vendidas * coalesce(costo_medio_periodo, 0), 2)
            as decimal(18, 2)) as costo_vendido
    from base
)
select
    *,
    facturacion_neta - costo_vendido as ganancia_bruta,
    round(100.0 * (facturacion_neta - costo_vendido) / nullif(facturacion_neta, 0), 2)
        as margen_bruto_pct
from costeadas
