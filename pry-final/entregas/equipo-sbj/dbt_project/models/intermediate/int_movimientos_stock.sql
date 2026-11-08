-- Movimientos de almacén con signo y stock acumulado por producto.
-- El orden (fecha, id) respeta la secuencia real de las operaciones.
with movimientos as (

    select
        m.movimiento_id,
        m.fecha_movimiento,
        m.producto_id,
        p.nombre_producto,
        p.categoria,
        m.tipo,
        m.motivo,
        m.referencia_id,
        m.cantidad,
        case when m.tipo = 'entrada' then m.cantidad else -m.cantidad end as cantidad_con_signo
    from {{ ref('stg_movimientos_stock') }} as m
    inner join {{ ref('stg_productos') }} as p using (producto_id)

)

select
    *,
    sum(cantidad_con_signo) over (
        partition by producto_id
        order by fecha_movimiento, movimiento_id
        rows between unbounded preceding and current row
    ) as stock_acumulado
from movimientos
