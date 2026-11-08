-- Ranking de vendedores por facturación
select
    ranking,
    nombre_vendedor,
    sucursal,
    cantidad_ventas,
    facturacion,
    ticket_promedio
from analytics.mart_desempeno_vendedores
order by ranking;

-- Distribución ABC: cuántos productos hay en cada clase y qué parte de los ingresos aportan
select
    clase_abc,
    count(*) as productos,
    round(sum(participacion_pct), 1) as porcentaje_de_ingresos
from analytics.mart_clasificacion_abc
group by clase_abc
order by clase_abc;

-- Los 5 productos más rentables
select
    nombre_producto,
    categoria,
    ingresos,
    ganancia_bruta,
    margen_pct
from analytics.mart_rentabilidad_productos
order by ganancia_bruta desc
limit 5;