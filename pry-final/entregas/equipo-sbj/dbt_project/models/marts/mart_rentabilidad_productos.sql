-- Ganancia bruta por producto = ingreso neto (ya con descuentos) - costo de ventas.
with ventas as (

    select
        producto_id,
        count(*)            as num_ventas,
        sum(cantidad)       as unidades_vendidas,
        sum(importe_neto)   as ingreso_neto,
        sum(importe_descuento) as descuentos,
        sum(costo_ventas)   as costo_ventas,
        sum(ganancia_bruta) as ganancia_bruta
    from {{ ref('int_ventas_enriquecidas') }}
    group by producto_id

)

select
    p.producto_id,
    p.nombre_producto,
    p.categoria,
    p.costo_unitario,
    p.precio_venta,
    coalesce(v.num_ventas, 0)         as num_ventas,
    coalesce(v.unidades_vendidas, 0)  as unidades_vendidas,
    coalesce(v.ingreso_neto, 0)       as ingreso_neto,
    coalesce(v.descuentos, 0)         as descuentos,
    coalesce(v.costo_ventas, 0)       as costo_ventas,
    coalesce(v.ganancia_bruta, 0)     as ganancia_bruta,
    round(100.0 * v.ganancia_bruta / nullif(v.ingreso_neto, 0), 2) as margen_pct,
    rank() over (order by coalesce(v.ganancia_bruta, 0) desc)      as ranking_ganancia
from {{ ref('stg_productos') }} as p
left join ventas as v using (producto_id)
order by ranking_ganancia
