-- Grain: one row per return
with returns as (
    select * from {{ ref('stg_returns') }}
),

items as (
    select order_item_id, product_id, seller_id, order_id
    from {{ ref('stg_order_items') }}
)

select
    r.return_id as return_key,
    r.return_id,
    r.order_id as order_key,
    r.order_item_id as order_item_key,
    i.product_id as product_key,
    i.seller_id as seller_key,
    to_char(r.return_date_day, 'YYYYMMDD')::int as date_key,
    r.return_date,
    r.return_reason,
    r.refund_amount,
    r.return_status
from returns r
left join items i on r.order_item_id = i.order_item_id
