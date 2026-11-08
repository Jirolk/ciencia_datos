-- Falla si la participación de los productos no suma 100 % (tolerancia por redondeo)
-- o si la clase A está vacía.
select 'participacion_no_suma_100' as problema, sum(participacion_pct) as valor
from {{ ref('mart_clasificacion_abc') }}
having abs(sum(participacion_pct) - 100) > 0.1

union all

select 'clase_a_vacia' as problema, count(*) as valor
from {{ ref('mart_clasificacion_abc') }}
where clasificacion_abc = 'A'
having count(*) = 0
