select
    location_id as location_key,
    location_id,
    city,
    province,
    region,
    country,
    latitude,
    longitude
from {{ ref('stg_locations') }}
