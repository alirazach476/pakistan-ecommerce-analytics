select
    row_number() over (order by order_status) as order_status_key,
    order_status
from (
    select distinct order_status
    from {{ ref('stg_orders') }}
) x
