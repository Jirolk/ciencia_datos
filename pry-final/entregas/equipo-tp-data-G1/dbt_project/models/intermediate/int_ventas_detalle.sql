-- Cada venta con su producto, su vendedor y sus importes ya calculados.
select
    v.venta_id,
    v.fecha_venta,
    v.producto_id,
    p.nombre_producto,
    p.categoria,
    v.vendedor_id,
    v.cantidad,
    v.precio_unitario,
    v.descuento,
    v.cantidad * v.precio_unitario as importe_bruto,
    v.cantidad * v.precio_unitario * (1 - v.descuento) as importe_neto,
    v.cantidad * p.costo_unitario as costo_venta
from {{ ref('stg_ventas') }} as v
inner join {{ ref('stg_productos') }} as p
    on v.producto_id = p.producto_id