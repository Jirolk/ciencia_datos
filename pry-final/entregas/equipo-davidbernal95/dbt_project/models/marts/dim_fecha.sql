-- Calendario completo: una fila por día, incluidos los días sin ventas.
select
    fecha,
    year(fecha) as anio,
    month(fecha) as mes,
    quarter(fecha) as trimestre,
    isodow(fecha) as dia_semana,
    isodow(fecha) >= 6 as es_fin_semana
from {{ ref('int_calendario') }}
