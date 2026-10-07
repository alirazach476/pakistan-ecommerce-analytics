select
    p.product_id as product_key,
    p.product_id,
    p.product_name,
    p.category_id,
    c.category_name,
    p.seller_id,
    p.brand,
    p.unit_price,
    p.cost_price,
    p.weight_kg,
    p.is_active,
    coalesce(pm.units_sold, 0) as units_sold,
    coalesce(pm.revenue, 0) as revenue,
    coalesce(pm.net_revenue, 0) as net_revenue,
    coalesce(pm.return_rate, 0) as return_rate,
    coalesce(pm.cancellation_rate, 0) as cancellation_rate
from {{ ref('stg_products') }} p
left join {{ ref('stg_categories') }} c on p.category_id = c.category_id
left join {{ ref('int_product_metrics') }} pm on p.product_id = pm.product_id
