with source as (
    select * from {{ source('raw', 'locations') }}
)

select
    location_id,
    city,
    province,
    region,
    country,
    latitude,
    longitude,
    loaded_at,
    source_file
from source
