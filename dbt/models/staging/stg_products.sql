with source as (
    select * from {{ source('raw', 'products') }}
)

select
    product_id,
    product_name,
    category_id,
    seller_id,
    brand,
    unit_price::numeric(12, 2) as unit_price,
    cost_price::numeric(12, 2) as cost_price,
    weight_kg,
    coalesce(is_active, true) as is_active,
    created_at,
    updated_at,
    loaded_at,
    source_file
from source
where unit_price >= 0
