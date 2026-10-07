with items as (
    select
        order_id,
        count(*) as item_count,
        sum(quantity) as total_units,
        sum(gross_revenue) as gross_revenue,
        sum(discount_amount) as item_discount_amount,
        sum(net_line_revenue) as net_item_revenue
    from {{ ref('stg_order_items') }}
    group by 1
),

refunds as (
    select
        order_id,
        sum(refund_amount) as refund_amount,
        count(*) as return_count
    from {{ ref('stg_returns') }}
    group by 1
),

orders as (
    select * from {{ ref('stg_orders') }}
)

select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_date_day,
    o.order_status,
    o.location_id,
    o.shipping_fee,
    o.discount_amount as order_discount_amount,
    o.total_amount,
    o.currency,
    coalesce(i.item_count, 0) as item_count,
    coalesce(i.total_units, 0) as total_units,
    coalesce(i.gross_revenue, 0) as gross_revenue,
    coalesce(i.item_discount_amount, 0) as item_discount_amount,
    coalesce(i.net_item_revenue, 0) as net_item_revenue,
    coalesce(r.refund_amount, 0) as refund_amount,
    coalesce(r.return_count, 0) as return_count,
    coalesce(i.net_item_revenue, 0) - coalesce(r.refund_amount, 0) as net_revenue,
    case when o.order_status = 'Delivered' then 1 else 0 end as is_completed,
    case when o.order_status = 'Cancelled' then 1 else 0 end as is_cancelled,
    case when o.order_status = 'Returned' or coalesce(r.return_count, 0) > 0 then 1 else 0 end as is_returned
from orders o
left join items i on o.order_id = i.order_id
left join refunds r on o.order_id = r.order_id
