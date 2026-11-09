select
    clase_abc,
    count(*) as productos,
    sum(unidades_vendidas) as unidades,
    sum(facturacion_neta) as facturacion_neta,
    round(100.0 * sum(facturacion_neta)
        / nullif(sum(sum(facturacion_neta)) over (), 0), 2) as porcentaje_facturacion
from analitica.mart_abc_productos
group by clase_abc
order by clase_abc;
