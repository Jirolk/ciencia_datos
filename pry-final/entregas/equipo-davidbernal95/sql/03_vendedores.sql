select
    row_number() over (order by facturacion_neta desc, vendedor_id) as puesto,
    vendedor,
    unidades_vendidas,
    facturacion_neta
from analitica.mart_desempeno_vendedores
order by puesto;
