select 'venta' as entidad, venta_id as id
from {{ ref('stg_ventas') }}
where cantidad <= 0 or precio_unitario <= 0 or descuento < 0 or descuento >= 1
    or importe_neto <= 0

union all
select 'compra', compra_id
from {{ ref('stg_compras') }}
where cantidad <= 0 or costo_unitario <= 0

union all
select 'producto', producto_id
from {{ ref('stg_productos') }}
where costo_inicial <= 0 or precio_lista <= 0 or stock_inicial < 0

union all
select 'venta_antes_alta', v.venta_id
from {{ ref('stg_ventas') }} v
join {{ ref('stg_vendedores') }} e using (vendedor_id)
where v.fecha < e.fecha_alta
