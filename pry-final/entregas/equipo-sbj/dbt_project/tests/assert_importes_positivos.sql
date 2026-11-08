-- Falla si alguna venta o compra tiene cantidades/importes no positivos
-- o un descuento fuera del rango [0, 1).
select 'ventas' as origen, venta_id as id
from {{ ref('stg_ventas') }}
where cantidad <= 0 or precio_unitario <= 0 or importe_neto <= 0 or descuento < 0 or descuento >= 1

union all

select 'compras' as origen, compra_id as id
from {{ ref('stg_compras') }}
where cantidad <= 0 or costo_unitario <= 0 or importe_compra <= 0
