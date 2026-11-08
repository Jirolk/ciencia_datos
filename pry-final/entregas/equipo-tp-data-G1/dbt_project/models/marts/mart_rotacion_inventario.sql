-- Rotación = unidades vendidas / stock promedio, con stock promedio = (inicial + final) / 2.
-- Días de stock = stock final / venta diaria promedio.
with stock_final as (

    select
        producto_id,
        arg_max(stock_despues, (fecha, case when tipo = 'entrada' then 0 else 1 end, referencia)) as stock_final
    from {{ ref('int_movimientos_stock') }}
    group by producto_id

),

ventas as (

    select producto_id, sum(cantidad) as unidades_vendidas
    from {{ ref('stg_ventas') }}
    group by producto_id

),

periodo as (

    select date_diff('day', min(fecha_venta), max(fecha_venta)) + 1 as dias
    from {{ ref('stg_ventas') }}

),

base as (

    select
        p.producto_id,
        p.nombre_producto,
        p.categoria,
        p.stock_inicial,
        s.stock_final,
        coalesce(v.unidades_vendidas, 0) as unidades_vendidas,
        coalesce(v.unidades_vendidas, 0) * 1.0 / periodo.dias as venta_diaria_promedio
    from {{ ref('stg_productos') }} as p
    inner join stock_final as s on p.producto_id = s.producto_id
    left join ventas as v on p.producto_id = v.producto_id
    cross join periodo

)

select
    producto_id,
    nombre_producto,
    categoria,
    stock_inicial,
    stock_final,
    unidades_vendidas,
    round(venta_diaria_promedio, 2) as venta_diaria_promedio,
    round(unidades_vendidas / nullif((stock_inicial + stock_final) / 2.0, 0), 2) as rotacion,
    round(stock_final / nullif(venta_diaria_promedio, 0), 1) as dias_de_stock,
    ceil(venta_diaria_promedio * {{ var('dias_cobertura_reposicion') }}) as punto_reposicion,
    stock_final < ceil(venta_diaria_promedio * {{ var('dias_cobertura_reposicion') }}) as bajo_punto_reposicion
from base
order by dias_de_stock