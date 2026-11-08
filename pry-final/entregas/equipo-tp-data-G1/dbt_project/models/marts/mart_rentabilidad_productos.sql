select
    producto_id,
    nombre_producto,
    categoria,
    sum(cantidad) as unidades_vendidas,
    sum(importe_neto) as ingresos,
    sum(costo_venta) as costo_total,
    sum(importe_neto) - sum(costo_venta) as ganancia_bruta,
    round((sum(importe_neto) - sum(costo_venta)) / nullif(sum(importe_neto), 0) * 100, 2) as margen_pct
from {{ ref('int_ventas_detalle') }}
group by producto_id, nombre_producto, categoria
order by ganancia_bruta desc