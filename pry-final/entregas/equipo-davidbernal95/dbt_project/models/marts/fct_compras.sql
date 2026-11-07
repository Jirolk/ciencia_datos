-- Grano: una línea de compra de un producto a un proveedor.
select
    compra_id,
    fecha,
    producto_id,
    cantidad,
    costo_unitario,
    proveedor,
    cast(cantidad * costo_unitario as decimal(18, 2)) as costo_total
from {{ ref('stg_compras') }}
