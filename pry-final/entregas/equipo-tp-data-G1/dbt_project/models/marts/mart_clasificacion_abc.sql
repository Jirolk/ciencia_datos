-- ABC por ingresos: A = productos que juntos llegan al 80 %, B = hasta el 95 %, C = el resto.
-- Un producto entra a A si el acumulado ANTES de él todavía no llegaba al 80 %.
with ingresos as (

    select producto_id, nombre_producto, categoria, sum(importe_neto) as ingresos
    from {{ ref('int_ventas_detalle') }}
    group by producto_id, nombre_producto, categoria

),

acumulado as (

    select
        *,
        ingresos / sum(ingresos) over () as participacion,
        sum(ingresos) over (order by ingresos desc, producto_id) / sum(ingresos) over () as participacion_acumulada
    from ingresos

)

select
    producto_id,
    nombre_producto,
    categoria,
    ingresos,
    round(participacion * 100, 2) as participacion_pct,
    round(participacion_acumulada * 100, 2) as acumulada_pct,
    case
        when participacion_acumulada - participacion < 0.80 then 'A'
        when participacion_acumulada - participacion < 0.95 then 'B'
        else 'C'
    end as clase_abc
from acumulado
order by ingresos desc