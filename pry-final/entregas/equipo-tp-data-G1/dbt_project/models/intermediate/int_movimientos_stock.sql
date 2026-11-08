-- Une compras (entradas) y ventas (salidas) en un solo historial por producto
-- y calcula cuánto stock había después de cada movimiento.
with movimientos as (

    select
        fecha_compra as fecha,
        producto_id,
        'entrada' as tipo,
        cantidad,
        cantidad as cantidad_con_signo,
        'compra-' || compra_id as referencia
    from {{ ref('stg_compras') }}

    union all

    select
        fecha_venta as fecha,
        producto_id,
        'salida' as tipo,
        cantidad,
        -cantidad as cantidad_con_signo,
        'venta-' || venta_id as referencia
    from {{ ref('stg_ventas') }}

),

con_stock as (

    select
        m.fecha,
        m.producto_id,
        m.tipo,
        m.cantidad,
        m.cantidad_con_signo,
        m.referencia,
        p.stock_inicial
            + sum(m.cantidad_con_signo) over (
                partition by m.producto_id
                -- Dentro de un día, primero llegan las compras y luego se vende.
                order by m.fecha, case when m.tipo = 'entrada' then 0 else 1 end, m.referencia
            ) as stock_despues
    from movimientos as m
    inner join {{ ref('stg_productos') }} as p
        on m.producto_id = p.producto_id

)

select * from con_stock