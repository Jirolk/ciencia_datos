-- Rotación y cobertura de inventario por producto.
--   venta_diaria_reciente = unidades vendidas en los últimos `ventana_dias` / ventana_dias
--   dias_de_stock         = stock_actual / venta_diaria_reciente
--   rotacion              = unidades vendidas del período / stock promedio
--                           (stock promedio = (stock inicial + stock actual) / 2)
--   punto_reposicion      = venta_diaria_reciente × (dias_reposicion + dias_seguridad)
with fin as (

    select max(fecha_movimiento) as fecha_fin
    from {{ ref('int_movimientos_stock') }}

),

stock_actual as (

    select producto_id, stock_acumulado as stock_actual
    from {{ ref('int_movimientos_stock') }}
    qualify row_number() over (
        partition by producto_id order by fecha_movimiento desc, movimiento_id desc
    ) = 1

),

ventas_totales as (

    select producto_id, sum(cantidad) as unidades_periodo
    from {{ ref('int_ventas_enriquecidas') }}
    group by producto_id

),

ventas_recientes as (

    select v.producto_id, sum(v.cantidad) as unidades_ventana
    from {{ ref('int_ventas_enriquecidas') }} as v
    cross join fin
    where v.fecha_venta > fin.fecha_fin - {{ var('ventana_dias') }}
    group by v.producto_id

)

select
    p.producto_id,
    p.nombre_producto,
    p.categoria,
    p.stock_inicial,
    s.stock_actual,
    coalesce(t.unidades_periodo, 0)                                               as unidades_vendidas,
    round(coalesce(r.unidades_ventana, 0) * 1.0 / {{ var('ventana_dias') }}, 2)   as venta_diaria_reciente,
    round(s.stock_actual / nullif(coalesce(r.unidades_ventana, 0) * 1.0 / {{ var('ventana_dias') }}, 0), 1)
                                                                                  as dias_de_stock,
    round(coalesce(t.unidades_periodo, 0) / ((p.stock_inicial + s.stock_actual) / 2.0), 2)
                                                                                  as rotacion,
    cast(ceil(coalesce(r.unidades_ventana, 0) * 1.0 / {{ var('ventana_dias') }}
              * ({{ var('dias_reposicion') }} + {{ var('dias_seguridad') }})) as integer)
                                                                                  as punto_reposicion,
    s.stock_actual < ceil(coalesce(r.unidades_ventana, 0) * 1.0 / {{ var('ventana_dias') }}
                          * ({{ var('dias_reposicion') }} + {{ var('dias_seguridad') }}))
                                                                                  as bajo_punto_reposicion
from {{ ref('stg_productos') }} as p
inner join stock_actual as s using (producto_id)
left join ventas_totales as t using (producto_id)
left join ventas_recientes as r using (producto_id)
order by dias_de_stock
