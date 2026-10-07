-- Business rule: order total_amount must be >= 0
select order_id, total_amount
from {{ ref('fact_orders') }}
where total_amount < 0
