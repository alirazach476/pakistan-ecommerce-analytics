with source as (
    select * from {{ source('raw', 'orders') }}
)

select
    order_id,
    customer_id,
    order_date::timestamp as order_date,
    order_date::date as order_date_day,
    order_status,
    location_id,
    shipping_fee::numeric(12, 2) as shipping_fee,
    discount_amount::numeric(12, 2) as discount_amount,
    total_amount::numeric(14, 2) as total_amount,
    currency,
    created_at,
    updated_at,
    loaded_at,
    source_file
from source
where total_amount >= 0
