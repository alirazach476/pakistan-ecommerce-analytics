-- Grain: one row per order
with orders as (
    select * from {{ ref('int_order_metrics') }}
),

status_dim as (
    select * from {{ ref('dim_order_status') }}
)

select
    o.order_id as order_key,
    o.order_id,
    o.customer_id as customer_key,
    o.location_id as location_key,
    to_char(o.order_date_day, 'YYYYMMDD')::int as date_key,
    s.order_status_key,
    o.order_status,
    o.order_date,
    o.shipping_fee,
    o.order_discount_amount as discount_amount,
    o.total_amount,
    o.item_count,
    o.total_units,
    o.gross_revenue,
    o.refund_amount,
    o.net_revenue,
    o.is_completed,
    o.is_cancelled,
    o.is_returned,
    o.currency
from orders o
left join status_dim s on o.order_status = s.order_status
