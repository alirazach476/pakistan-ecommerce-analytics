select
    customer_key,
    customer_id,
    customer_segment,
    rfm_segment,
    recency_score,
    frequency_score,
    monetary_score,
    rfm_score,
    customer_lifetime_value,
    total_orders,
    total_spend,
    days_since_last_order
from {{ ref('dim_customer') }}
where total_orders > 0
