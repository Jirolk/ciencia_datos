-- Resumen diario. Incluye TODOS los días del período (también los sin ventas,
-- con ceros) para que promedio, mediana y desviación estándar no se sesguen.
with limites as (

    select min(fecha_venta) as desde, max(fecha_venta) as hasta
    from {{ ref('int_ventas_enriquecidas') }}

),

calendario as (

    select cast(unnest(generate_series(desde, hasta, interval 1 day)) as date) as fecha
    from limites

),

agregado as (

    select
        fecha_venta,
        count(*)                as num_ventas,
        sum(cantidad)           as unidades_vendidas,
        sum(importe_bruto)      as ingreso_bruto,
        sum(importe_descuento)  as descuentos,
        sum(importe_neto)       as ingreso_neto,
        sum(costo_ventas)       as costo_ventas,
        sum(ganancia_bruta)     as ganancia_bruta
    from {{ ref('int_ventas_enriquecidas') }}
    group by fecha_venta

)

select
    c.fecha,
    case isodow(c.fecha)
        when 1 then 'lunes' when 2 then 'martes' when 3 then 'miércoles' when 4 then 'jueves'
        when 5 then 'viernes' when 6 then 'sábado' else 'domingo'
    end                                               as dia_semana,
    isodow(c.fecha)                                   as dia_semana_num,
    coalesce(a.num_ventas, 0)                         as num_ventas,
    coalesce(a.unidades_vendidas, 0)                  as unidades_vendidas,
    coalesce(a.ingreso_bruto, 0)                      as ingreso_bruto,
    coalesce(a.descuentos, 0)                         as descuentos,
    coalesce(a.ingreso_neto, 0)                       as ingreso_neto,
    coalesce(a.costo_ventas, 0)                       as costo_ventas,
    coalesce(a.ganancia_bruta, 0)                     as ganancia_bruta,
    round(a.ingreso_neto / nullif(a.num_ventas, 0), 2) as ticket_promedio
from calendario as c
left join agregado as a on a.fecha_venta = c.fecha
order by c.fecha
