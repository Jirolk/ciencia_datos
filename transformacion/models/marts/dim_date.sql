select distinct
    sale_date as date_key,
    year(sale_date) as sale_year,
    month(sale_date) as sale_month,
    quarter(sale_date) as sale_quarter
from {{ ref('stg_car_sales') }}