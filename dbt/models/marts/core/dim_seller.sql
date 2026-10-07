with sellers as (
    select * from {{ ref('stg_sellers') }}
),

metrics as (
    select
        seller_id,
        sum(net_line_revenue) as seller_revenue,
        count(distinct order_id) as seller_orders
    from {{ ref('stg_order_items') }}
    group by 1
),

returns as (
    select
        oi.seller_id,
        count(r.return_id)::numeric / nullif(count(distinct oi.order_item_id), 0) as seller_return_rate
    from {{ ref('stg_order_items') }} oi
    left join {{ ref('stg_returns') }} r on oi.order_item_id = r.order_item_id
    group by 1
),

cancels as (
    select
        oi.seller_id,
        sum(case when o.order_status = 'Cancelled' then 1 else 0 end)::numeric
            / nullif(count(*), 0) as seller_cancellation_rate
    from {{ ref('stg_order_items') }} oi
    inner join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
    group by 1
)

select
    s.seller_id as seller_key,
    s.seller_id,
    s.seller_name,
    s.business_type,
    s.location_id,
    s.registration_date,
    s.is_active,
    s.rating,
    coalesce(m.seller_revenue, 0) as seller_revenue,
    coalesce(m.seller_orders, 0) as seller_orders,
    coalesce(r.seller_return_rate, 0) as seller_return_rate,
    coalesce(c.seller_cancellation_rate, 0) as seller_cancellation_rate,
    case
        when coalesce(m.seller_revenue, 0) >= 5000000
             and coalesce(r.seller_return_rate, 0) <= 0.08
             and coalesce(c.seller_cancellation_rate, 0) <= 0.05
            then 'Platinum'
        when coalesce(m.seller_revenue, 0) >= 2000000
             and coalesce(r.seller_return_rate, 0) <= 0.12
             and coalesce(c.seller_cancellation_rate, 0) <= 0.08
            then 'Gold'
        when coalesce(m.seller_revenue, 0) >= 500000
            then 'Silver'
        else 'Bronze'
    end as seller_tier
from sellers s
left join metrics m on s.seller_id = m.seller_id
left join returns r on s.seller_id = r.seller_id
left join cancels c on s.seller_id = c.seller_id
