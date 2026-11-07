select producto, unidades_vendidas, facturacion_neta,
       costo_vendido, ganancia_bruta, margen_bruto_pct
from analitica.mart_rentabilidad_productos
order by ganancia_bruta desc, producto_id;
