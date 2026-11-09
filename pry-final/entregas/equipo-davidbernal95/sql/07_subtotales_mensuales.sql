-- Detalle mensual por categoría, subtotal por mes y total general.
select
    d.anio,
    d.mes,
    p.categoria,
    grouping(d.mes) = 1 as es_total_general,
    grouping(p.categoria) = 1 as es_subtotal,
    sum(f.cantidad) as unidades,
    sum(f.importe_neto) as facturacion_neta
from analitica.fct_ventas f
join analitica.dim_fecha d using (fecha)
join analitica.dim_productos p using (producto_id)
group by grouping sets ((d.anio, d.mes, p.categoria), (d.anio, d.mes), ())
order by grouping(d.mes), d.anio, d.mes, grouping(p.categoria), p.categoria;
