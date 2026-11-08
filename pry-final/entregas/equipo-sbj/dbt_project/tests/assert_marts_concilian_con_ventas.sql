-- Falla si el ingreso neto total de algún mart difiere del total de stg_ventas,
-- o si el ingreso/ganancia de los marts no cuadran entre sí.
with referencia as (
    select sum(importe_neto) as ingreso_neto from {{ ref('stg_ventas') }}
),

totales as (
    select 'ventas_diarias' as mart, sum(ingreso_neto) as ingreso_neto from {{ ref('mart_ventas_diarias') }}
    union all
    select 'rentabilidad_productos', sum(ingreso_neto) from {{ ref('mart_rentabilidad_productos') }}
    union all
    select 'desempeno_vendedores', sum(ingreso_neto) from {{ ref('mart_desempeno_vendedores') }}
    union all
    select 'clasificacion_abc', sum(ingreso_neto) from {{ ref('mart_clasificacion_abc') }}
)

select t.mart, t.ingreso_neto, r.ingreso_neto as ingreso_referencia
from totales as t
cross join referencia as r
where abs(t.ingreso_neto - r.ingreso_neto) > 0.01
