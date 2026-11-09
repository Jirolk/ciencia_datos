-- Grano: una línea vendida de un producto, con su fecha y vendedor.
select
    venta_id,
    fecha,
    producto_id,
    vendedor_id,
    cantidad,
    precio_unitario,
    descuento,
    importe_bruto,
    importe_neto
from {{ ref('stg_ventas') }}
