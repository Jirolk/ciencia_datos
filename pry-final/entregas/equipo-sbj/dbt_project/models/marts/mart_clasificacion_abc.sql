-- Clasificación ABC (Pareto) por ingreso neto.
-- Regla: un producto es A si el acumulado ANTERIOR a él es < 80 %,
-- B si es < 95 % y C en el resto. Así el producto que cruza el umbral
-- queda en la clase superior y la clase A nunca queda vacía.
with ingreso as (

    select
        producto_id,
        nombre_producto,
        categoria,
        unidades_vendidas,
        ingreso_neto
    from {{ ref('mart_rentabilidad_productos') }}

),

participacion as (

    select
        *,
        ingreso_neto / sum(ingreso_neto) over ()  as participacion
    from ingreso

),

acumulado as (

    select
        *,
        sum(participacion) over (
            order by ingreso_neto desc, producto_id
            rows between unbounded preceding and current row
        ) as participacion_acumulada
    from participacion

)

select
    producto_id,
    nombre_producto,
    categoria,
    unidades_vendidas,
    ingreso_neto,
    round(100 * participacion, 2)            as participacion_pct,
    round(100 * participacion_acumulada, 2)  as participacion_acumulada_pct,
    case
        when participacion_acumulada - participacion < 0.80 then 'A'
        when participacion_acumulada - participacion < 0.95 then 'B'
        else 'C'
    end as clasificacion_abc
from acumulado
order by ingreso_neto desc, producto_id
