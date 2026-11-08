select
    fecha_venta as fecha,
    count(*) as cantidad_ventas,
    sum(cantidad) as unidades_vendidas,
    sum(importe_bruto) as importe_bruto,
    sum(importe_bruto - importe_neto) as descuentos,
    sum(importe_neto) as facturacion
from {{ ref('int_ventas_detalle') }}
group by fecha_venta
order by fecha_venta