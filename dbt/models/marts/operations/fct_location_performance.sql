with orders as (
    select * from {{ ref('fact_orders') }}
),

shipments as (
    select * from {{ ref('fact_shipments') }}
),

locations as (
    select * from {{ ref('dim_location') }}
)

select
    l.location_key,
    l.city,
    l.province,
    l.region,
    count(distinct o.order_id) as orders,
    count(distinct o.customer_key) as customers,
    sum(o.gross_revenue) as revenue,
    sum(o.net_revenue) as net_revenue,
    avg(o.total_amount) as aov,
    avg(s.total_delivery_days) as avg_delivery_days,
    avg(s.on_time_flag::numeric) as on_time_delivery_rate,
    sum(o.is_cancelled)::numeric / nullif(count(*), 0) as cancellation_rate,
    sum(o.is_returned)::numeric / nullif(count(*), 0) as return_rate
from locations l
left join orders o on l.location_key = o.location_key
left join shipments s on o.order_key = s.order_key
group by 1, 2, 3, 4
