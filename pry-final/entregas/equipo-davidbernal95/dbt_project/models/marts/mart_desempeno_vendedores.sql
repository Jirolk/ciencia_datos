select
    v.vendedor_id,
    v.vendedor,
    v.sucursal,
    count(x.venta_id) as lineas_venta,
    coalesce(sum(x.cantidad), 0) as unidades_vendidas,
    coalesce(sum(x.importe_neto), 0) as facturacion_neta,
    round(avg(x.importe_neto), 2) as importe_promedio_linea
from {{ ref('dim_vendedores') }} v
left join {{ ref('fct_ventas') }} x on v.vendedor_id = x.vendedor_id
group by v.vendedor_id, v.vendedor, v.sucursal
