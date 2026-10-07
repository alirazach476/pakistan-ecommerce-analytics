with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    customer_id,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    email,
    phone,
    gender,
    birth_date::date as birth_date,
    location_id,
    registration_date::date as registration_date,
    coalesce(is_active, true) as is_active,
    created_at,
    updated_at,
    loaded_at,
    source_file
from source
