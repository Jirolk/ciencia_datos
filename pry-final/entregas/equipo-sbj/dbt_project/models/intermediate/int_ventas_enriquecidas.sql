-- Ventas unidas a producto y vendedor, con costo y ganancia bruta por línea.
-- Costo de ventas = cantidad × costo_unitario del catálogo de productos.
select
    v.venta_id,
    v.fecha_venta,
    v.producto_id,
    p.nombre_producto,
    p.categoria,
    v.vendedor_id,
    s.nombre_vendedor,
    s.sucursal,
    v.cantidad,
    v.precio_unitario,
    v.descuento,
    v.importe_bruto,
    v.importe_descuento,
    v.importe_neto,
    cast(v.cantidad * p.costo_unitario as decimal(14, 2))                  as costo_ventas,
    cast(v.importe_neto - v.cantidad * p.costo_unitario as decimal(14, 2)) as ganancia_bruta
from {{ ref('stg_ventas') }} as v
inner join {{ ref('stg_productos') }} as p using (producto_id)
inner join {{ ref('stg_vendedores') }} as s using (vendedor_id)
