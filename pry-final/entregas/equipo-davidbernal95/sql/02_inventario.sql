select
    producto,
    stock_actual,
    dias_con_stock,
    dias_cobertura,
    rotacion_unidades,
    punto_reposicion,
    bajo_reposicion
from analitica.mart_rotacion_inventario
order by bajo_reposicion desc, dias_cobertura asc nulls last, producto_id;
