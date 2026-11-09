select
    c.fecha,
    count(v.venta_id) as lineas_venta,
    coalesce(sum(v.cantidad), 0) as unidades_vendidas,
    coalesce(sum(v.importe_bruto), 0) as facturacion_bruta,
    coalesce(sum(v.importe_neto), 0) as facturacion_neta,
    coalesce(sum(v.importe_bruto - v.importe_neto), 0) as descuentos,
    round(avg(v.importe_neto), 2) as importe_promedio_linea
from {{ ref('dim_fecha') }} c
left join {{ ref('fct_ventas') }} v on c.fecha = v.fecha
group by c.fecha
