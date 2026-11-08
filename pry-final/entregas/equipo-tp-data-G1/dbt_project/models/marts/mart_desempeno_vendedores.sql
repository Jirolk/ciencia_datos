select
    v.vendedor_id,
    v.nombre_vendedor,
    v.sucursal,
    count(d.venta_id) as cantidad_ventas,
    coalesce(sum(d.cantidad), 0) as unidades_vendidas,
    coalesce(sum(d.importe_neto), 0) as facturacion,
    round(coalesce(sum(d.importe_neto), 0) / nullif(count(d.venta_id), 0), 0) as ticket_promedio,
    rank() over (order by coalesce(sum(d.importe_neto), 0) desc) as ranking
from {{ ref('stg_vendedores') }} as v
left join {{ ref('int_ventas_detalle') }} as d
    on v.vendedor_id = d.vendedor_id
group by v.vendedor_id, v.nombre_vendedor, v.sucursal
order by ranking