with items as (
    select
        oi.order_item_id,
        oi.order_id,
        oi.product_id,
        oi.quantity,
        oi.unit_price,
        oi.gross_revenue,
        oi.net_line_revenue,
        o.order_status,
        o.customer_id
    from {{ ref('stg_order_items') }} oi
    inner join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
),

refunds as (
    select
        order_item_id,
        sum(refund_amount) as refund_amount,
        count(*) as return_count
    from {{ ref('stg_returns') }}
    group by 1
)

select
    i.product_id,
    count(distinct i.order_id) as number_of_orders,
    count(distinct i.customer_id) as unique_customers,
    sum(i.quantity) as units_sold,
    sum(i.gross_revenue) as revenue,
    sum(i.net_line_revenue) - coalesce(sum(r.refund_amount), 0) as net_revenue,
    avg(i.unit_price) as average_price,
    sum(case when i.order_status = 'Cancelled' then 1 else 0 end)::numeric
        / nullif(count(*), 0) as cancellation_rate,
    coalesce(sum(r.return_count), 0)::numeric
        / nullif(count(*), 0) as return_rate
from items i
left join refunds r on i.order_item_id = r.order_item_id
group by 1
