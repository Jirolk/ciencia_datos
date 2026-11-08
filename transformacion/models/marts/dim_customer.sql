with stg as (
    select distinct
        customer_id,
        customer_name
    from {{ ref('stg_car_sales') }}
)

select
    customer_id,
    customer_name
from stg