-- Facturación total y unidades vendidas
select
    sum(facturacion) as facturacion_total,
    sum(unidades_vendidas) as unidades_vendidas,
    sum(cantidad_ventas) as cantidad_ventas
from analytics.mart_ventas_diarias;

-- Facturación diaria: promedio, mediana y desviación estándar
select
    count(*) as dias,
    round(avg(facturacion), 0) as promedio_diario,
    round(median(facturacion), 0) as mediana_diaria,
    round(stddev_samp(facturacion), 0) as desviacion_estandar,
    round(stddev_samp(facturacion) / avg(facturacion) * 100, 1) as coef_variacion_pct,
    min(facturacion) as dia_minimo,
    max(facturacion) as dia_maximo
from analytics.mart_ventas_diarias;

-- Facturación promedio según el día de la semana
select
    dayname(fecha) as dia_semana,
    round(avg(facturacion), 0) as facturacion_promedio
from analytics.mart_ventas_diarias
group by dayname(fecha), isodow(fecha)
order by isodow(fecha);