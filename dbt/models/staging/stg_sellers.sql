with source as (
    select * from {{ source('raw', 'sellers') }}
)

select
    seller_id,
    seller_name,
    business_type,
    location_id,
    registration_date::date as registration_date,
    coalesce(is_active, true) as is_active,
    rating,
    created_at,
    updated_at,
    loaded_at,
    source_file
from source
