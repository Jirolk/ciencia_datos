with stg as (
    select distinct
        car_make,
        car_model,
        car_year
    from {{ ref('stg_car_sales') }}
)

select
    -- el vehículo no trae ID de origen: clave subrogada (hash)
    {{ dbt_utils.generate_surrogate_key(['car_make', 'car_model', 'car_year']) }} as car_key,
    car_make,
    car_model,
    car_year
from stg