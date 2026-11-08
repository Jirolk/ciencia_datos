-- Rotación de inventario y días de stock por producto (menos días de stock primero)
select
    nombre_producto,
    stock_final,
    unidades_vendidas,
    rotacion,
    dias_de_stock
from analytics.mart_rotacion_inventario
order by dias_de_stock
limit 10;

-- Productos por debajo del punto de reposición
select
    nombre_producto,
    stock_final,
    punto_reposicion,
    venta_diaria_promedio,
    dias_de_stock
from analytics.mart_rotacion_inventario
where bajo_punto_reposicion
order by dias_de_stock;