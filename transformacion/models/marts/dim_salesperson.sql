with stg as (
    select distinct
        salesperson_id,
        salesperson_name
    from {{ ref('stg_car_sales') }}
)

select
    salesperson_id,
    salesperson_name
from stg