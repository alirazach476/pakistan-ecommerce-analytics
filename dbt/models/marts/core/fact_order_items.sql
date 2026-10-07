-- Grain: one row per order item
with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select order_id, order_date_day, order_status, customer_id, location_id
    from {{ ref('stg_orders') }}
),

refunds as (
    select
        order_item_id,
        sum(refund_amount) as refund_amount
    from {{ ref('stg_returns') }}
    group by 1
)

select
    i.order_item_id as order_item_key,
    i.order_item_id,
    i.order_id as order_key,
    i.product_id as product_key,
    i.seller_id as seller_key,
    o.customer_id as customer_key,
    o.location_id as location_key,
    to_char(o.order_date_day, 'YYYYMMDD')::int as date_key,
    o.order_status,
    i.quantity,
    i.unit_price,
    i.discount_amount,
    i.line_total,
    i.gross_revenue,
    coalesce(r.refund_amount, 0) as refund_amount,
    i.net_line_revenue - coalesce(r.refund_amount, 0) as net_revenue
from items i
inner join orders o on i.order_id = o.order_id
left join refunds r on i.order_item_id = r.order_item_id
