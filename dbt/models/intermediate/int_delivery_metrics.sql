with orders as (
    select order_id, order_date, order_status, location_id, customer_id
    from {{ ref('stg_orders') }}
),

shipments as (
    select * from {{ ref('stg_shipments') }}
)

select
    o.order_id,
    o.customer_id,
    o.location_id,
    o.order_date,
    o.order_status,
    s.shipment_id,
    s.carrier,
    s.shipment_date,
    s.delivery_date,
    s.promised_delivery_date,
    s.delivery_status,
    case
        when s.shipment_date is not null
            then extract(epoch from (s.shipment_date - o.order_date)) / 86400.0
        else null
    end as order_to_ship_days,
    s.ship_to_delivery_days,
    case
        when s.delivery_date is not null
            then extract(epoch from (s.delivery_date - o.order_date)) / 86400.0
        else null
    end as total_delivery_days,
    case
        when s.delivery_date is not null and s.promised_delivery_date is not null
            then (s.delivery_date::date <= s.promised_delivery_date)
        else null
    end as on_time_flag,
    case
        when s.delivery_date is not null and s.promised_delivery_date is not null
             and s.delivery_date::date > s.promised_delivery_date
            then 1
        else 0
    end as is_delayed
from orders o
left join shipments s on o.order_id = s.order_id
