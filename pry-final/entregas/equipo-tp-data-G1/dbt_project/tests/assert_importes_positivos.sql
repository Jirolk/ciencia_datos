-- Falla si hay ventas con cantidad o importe que no sea positivo.
select *
from {{ ref('int_ventas_detalle') }}
where cantidad <= 0 or importe_neto <= 0