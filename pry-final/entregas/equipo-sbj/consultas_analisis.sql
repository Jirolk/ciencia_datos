-- Consultas SQL finales sobre los marts (esquema `marts` de data.duckdb).
-- Cada consulta empieza con un marcador `-- name: <id>` y termina en `;`.
-- Se ejecutan todas con:  python analisis.py

-- name: 1_descriptivo_global
-- Facturación total, unidades vendidas y ganancia del período.
select
    min(fecha)                         as desde,
    max(fecha)                         as hasta,
    count(*)                           as dias,
    sum(num_ventas)                    as num_ventas,
    sum(unidades_vendidas)             as unidades_vendidas,
    round(sum(ingreso_neto), 2)        as facturacion_total,
    round(sum(ganancia_bruta), 2)      as ganancia_bruta,
    round(100 * sum(ganancia_bruta) / sum(ingreso_neto), 2) as margen_bruto_pct
from marts.mart_ventas_diarias;

-- name: 2_estadisticas_ventas_diarias
-- Promedio, mediana y desviación estándar de las ventas diarias.
select
    round(avg(ingreso_neto), 2)          as ingreso_promedio,
    round(median(ingreso_neto), 2)       as ingreso_mediana,
    round(stddev_samp(ingreso_neto), 2)  as ingreso_desv_std,
    round(100 * stddev_samp(ingreso_neto) / avg(ingreso_neto), 1) as coef_variacion_pct,
    round(min(ingreso_neto), 2)          as ingreso_minimo,
    round(max(ingreso_neto), 2)          as ingreso_maximo,
    round(avg(unidades_vendidas), 1)     as unidades_promedio,
    round(median(unidades_vendidas), 1)  as unidades_mediana,
    round(stddev_samp(unidades_vendidas), 1) as unidades_desv_std
from marts.mart_ventas_diarias;

-- name: 3_ventas_por_dia_de_semana
-- Patrón semanal de la demanda.
select
    dia_semana,
    round(avg(ingreso_neto), 2) as ingreso_promedio,
    round(avg(num_ventas), 1)   as ventas_promedio
from marts.mart_ventas_diarias
group by dia_semana, dia_semana_num
order by dia_semana_num;

-- name: 4_rotacion_de_inventario
-- Rotación y cobertura (días de stock) por producto.
select producto_id, nombre_producto, stock_inicial, stock_actual,
       unidades_vendidas, rotacion, venta_diaria_reciente, dias_de_stock
from marts.mart_rotacion_inventario
order by rotacion desc;

-- name: 5_productos_bajo_punto_de_reposicion
-- Productos cuyo stock actual está por debajo del punto de reposición.
select producto_id, nombre_producto, stock_actual, punto_reposicion,
       dias_de_stock, punto_reposicion - stock_actual as faltante
from marts.mart_rotacion_inventario
where bajo_punto_reposicion
order by faltante desc;

-- name: 6_top_vendedores
-- Ranking de vendedores por ingreso neto.
select ranking, nombre_vendedor, sucursal, num_ventas, unidades_vendidas,
       ingreso_neto, ganancia_bruta, ticket_promedio, participacion_pct
from marts.mart_desempeno_vendedores
order by ranking;

-- name: 7_distribucion_abc
-- Cuántos productos hay por clase y cuánto ingreso concentran.
select
    clasificacion_abc,
    count(*)                         as productos,
    round(sum(ingreso_neto), 2)      as ingreso_neto,
    round(sum(participacion_pct), 2) as participacion_ingreso_pct,
    round(100.0 * count(*) / sum(count(*)) over (), 1) as participacion_productos_pct
from marts.mart_clasificacion_abc
group by clasificacion_abc
order by clasificacion_abc;

-- name: 8_top5_rentabilidad
-- Productos con mayor ganancia bruta y su margen.
select ranking_ganancia, nombre_producto, categoria, unidades_vendidas,
       ingreso_neto, ganancia_bruta, margen_pct
from marts.mart_rentabilidad_productos
order by ranking_ganancia
limit 5;

-- name: 9_margen_por_categoria
-- Rentabilidad agregada por categoría.
select categoria,
       round(sum(ingreso_neto), 2)   as ingreso_neto,
       round(sum(ganancia_bruta), 2) as ganancia_bruta,
       round(100 * sum(ganancia_bruta) / sum(ingreso_neto), 2) as margen_pct
from marts.mart_rentabilidad_productos
group by categoria
order by ganancia_bruta desc;
