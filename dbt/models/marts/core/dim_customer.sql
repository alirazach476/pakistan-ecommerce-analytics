with customers as (
    select * from {{ ref('stg_customers') }}
),

metrics as (
    select * from {{ ref('int_customer_metrics') }}
),

spend_ranks as (
    select
        customer_id,
        net_revenue,
        ntile(5) over (order by net_revenue desc) as monetary_quintile
    from metrics
),

rfm_base as (
    select
        m.customer_id,
        m.days_since_last_order as recency_days,
        m.total_orders as frequency,
        m.net_revenue as monetary,
        ntile(5) over (order by m.days_since_last_order asc) as recency_score,
        ntile(5) over (order by m.total_orders asc) as frequency_score,
        ntile(5) over (order by m.net_revenue asc) as monetary_score
    from metrics m
)

select
    c.customer_id as customer_key,
    c.customer_id,
    c.full_name,
    c.email,
    c.phone,
    c.gender,
    c.birth_date,
    c.location_id,
    c.registration_date,
    c.is_active,
    coalesce(m.total_orders, 0) as total_orders,
    coalesce(m.total_spend, 0) as total_spend,
    coalesce(m.average_order_value, 0) as average_order_value,
    m.first_order_date,
    m.last_order_date,
    m.days_since_last_order,
    coalesce(m.total_items, 0) as total_items,
    coalesce(m.return_count, 0) as return_count,
    coalesce(m.cancelled_orders, 0) as cancelled_orders,
    coalesce(m.customer_lifetime_value, 0) as customer_lifetime_value,
    case
        when coalesce(m.total_orders, 0) = 0 then 'Inactive'
        when coalesce(sr.monetary_quintile, 5) = 1 then 'High Value'
        when coalesce(m.total_orders, 0) = 1 and m.days_since_last_order <= 90 then 'New Customer'
        when coalesce(m.total_orders, 0) >= 2 and m.days_since_last_order <= 180 then 'Returning Customer'
        when coalesce(m.total_orders, 0) >= 2 and m.days_since_last_order between 91 and 180 then 'At Risk'
        when m.days_since_last_order > 180 then 'Inactive'
        else 'Returning Customer'
    end as customer_segment,
    r.recency_score,
    r.frequency_score,
    r.monetary_score,
    (coalesce(r.recency_score, 0) + coalesce(r.frequency_score, 0) + coalesce(r.monetary_score, 0)) as rfm_score,
    case
        when r.recency_score >= 4 and r.frequency_score >= 4 and r.monetary_score >= 4 then 'Champions'
        when r.recency_score >= 3 and r.frequency_score >= 3 and r.monetary_score >= 3 then 'Loyal Customers'
        when r.recency_score <= 2 and r.frequency_score >= 3 and r.monetary_score >= 3 then 'At Risk'
        when r.recency_score <= 2 and r.frequency_score <= 2 and r.monetary_score <= 2 then 'Lost'
        when r.recency_score = 3 and r.frequency_score <= 2 and r.monetary_score <= 2 then 'Needs Attention'
        when r.recency_score >= 3 and r.frequency_score >= 1 and r.monetary_score >= 2 then 'Potential Loyalists'
        else 'Needs Attention'
    end as rfm_segment
from customers c
left join metrics m on c.customer_id = m.customer_id
left join spend_ranks sr on c.customer_id = sr.customer_id
left join rfm_base r on c.customer_id = r.customer_id
