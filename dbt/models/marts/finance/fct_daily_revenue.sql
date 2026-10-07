select
    date_key,
    count(*) as orders,
    sum(gross_revenue) as gross_revenue,
    sum(discount_amount) as discount_amount,
    sum(refund_amount) as refund_amount,
    sum(net_revenue) as net_revenue,
    avg(total_amount) as average_order_value
from {{ ref('fact_orders') }}
group by 1
