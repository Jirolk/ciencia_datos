with raw_data as (
    select * from {{ source('bronze_raw', 'raw_car_sales') }}
)

select 
    -- fecha: texto MM/DD/YYYY -> DATE
    strptime("date", '%m/%d/%Y')::date as sale_date,

    -- vendedor: separar ID y nombre
    regexp_extract(salesperson, '(\d+)$')::int as salesperson_id,
    trim(regexp_replace(salesperson, '\s+\d+$', '')) as salesperson_name,

    -- cliente: separar ID y nombre
    regexp_extract(customer_name, '(\d+)$')::int as customer_id,
    trim(regexp_replace(customer_name, '\s+\d+$', '')) as customer_name,

    -- atributos del vehículo
    trim(car_make) as car_make,
    trim(car_model) as car_model,
    car_year::int as car_year,

    -- métricas
    sale_price::decimal(12, 2) as sale_price,
    commission_rate::decimal(5, 4) as commission_rate,
    commission_earned::decimal(12, 2) as commission_earned

from raw_data

where car_make != null and car_model != null

