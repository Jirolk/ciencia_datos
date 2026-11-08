{{ config(materialized='table') }}

with stg as (
    select * from {{ ref('stg_car_sales') }}
)

select
    -- claves foráneas hacia las dimensiones
    sale_date,
    salesperson_id,
    customer_id,
    {{ dbt_utils.generate_surrogate_key(['car_make', 'car_model', 'car_year']) }} as car_key,

    -- métricas aditivas
    sale_price,
    commission_rate,
    commission_earned
from stg
