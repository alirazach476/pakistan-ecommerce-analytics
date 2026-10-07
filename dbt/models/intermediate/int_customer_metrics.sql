with orders as (
    select * from {{ ref('int_order_metrics') }}
),

agg as (
    select
        customer_id,
        count(*) as total_orders,
        sum(is_completed) as completed_orders,
        sum(is_cancelled) as cancelled_orders,
        sum(is_returned) as returned_orders,
        sum(gross_revenue) as gross_revenue,
        sum(net_revenue) as net_revenue,
        sum(total_amount) as total_spend,
        sum(total_units) as total_items,
        sum(return_count) as return_count,
        min(order_date_day) as first_order_date,
        max(order_date_day) as last_order_date,
        avg(total_amount) as average_order_value
    from orders
    group by 1
)

select
    customer_id,
    total_orders,
    completed_orders,
    cancelled_orders,
    returned_orders,
    gross_revenue,
    net_revenue,
    total_spend,
    total_items,
    return_count,
    first_order_date,
    last_order_date,
    average_order_value,
    (current_date - last_order_date) as days_since_last_order,
    -- CLV proxy for this portfolio: historical net revenue (not predictive LTV)
    net_revenue as customer_lifetime_value
from agg
