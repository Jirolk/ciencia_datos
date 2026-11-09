select
    count(*) as dias,
    sum(facturacion_neta) as facturacion_total,
    sum(unidades_vendidas) as unidades_vendidas,
    sum(lineas_venta) as lineas_venta,
    round(sum(facturacion_neta) / nullif(sum(lineas_venta), 0), 2) as importe_promedio_linea,
    round(avg(facturacion_neta), 2) as promedio_diario,
    round(median(facturacion_neta), 2) as mediana_diaria,
    round(stddev_pop(facturacion_neta), 2) as desviacion_diaria
from analitica.mart_ventas_diarias;
