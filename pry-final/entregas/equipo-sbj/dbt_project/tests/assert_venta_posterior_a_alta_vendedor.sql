-- Falla si un vendedor registra ventas antes de su fecha de alta.
select v.venta_id, v.vendedor_id, v.fecha_venta, s.fecha_alta
from {{ ref('stg_ventas') }} as v
inner join {{ ref('stg_vendedores') }} as s using (vendedor_id)
where v.fecha_venta < s.fecha_alta
