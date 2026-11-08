select
    s.vendedor_id,
    s.nombre_vendedor,
    s.sucursal,
    s.fecha_alta,
    count(v.venta_id)                                         as num_ventas,
    coalesce(sum(v.cantidad), 0)                              as unidades_vendidas,
    coalesce(sum(v.importe_neto), 0)                          as ingreso_neto,
    coalesce(sum(v.ganancia_bruta), 0)                        as ganancia_bruta,
    round(sum(v.importe_neto) / nullif(count(v.venta_id), 0), 2) as ticket_promedio,
    round(100.0 * sum(v.importe_neto) / sum(sum(v.importe_neto)) over (), 2) as participacion_pct,
    rank() over (order by coalesce(sum(v.importe_neto), 0) desc)             as ranking
from {{ ref('stg_vendedores') }} as s
left join {{ ref('int_ventas_enriquecidas') }} as v using (vendedor_id)
group by s.vendedor_id, s.nombre_vendedor, s.sucursal, s.fecha_alta
order by ranking
