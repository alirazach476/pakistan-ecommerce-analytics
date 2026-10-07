with source as (
    select * from {{ source('raw', 'order_items') }}
)

select
    order_item_id,
    order_id,
    product_id,
    seller_id,
    quantity,
    unit_price::numeric(12, 2) as unit_price,
    discount_amount::numeric(12, 2) as discount_amount,
    line_total::numeric(14, 2) as line_total,
    (quantity * unit_price)::numeric(14, 2) as gross_revenue,
    (quantity * unit_price - discount_amount)::numeric(14, 2) as net_line_revenue,
    created_at,
    loaded_at,
    source_file
from source
where quantity > 0
  and unit_price >= 0
  and discount_amount >= 0
