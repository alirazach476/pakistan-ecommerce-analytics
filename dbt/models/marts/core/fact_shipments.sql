-- Grain: one row per shipment
select
    d.shipment_id as shipment_key,
    d.shipment_id,
    d.order_id as order_key,
    d.customer_id as customer_key,
    d.location_id as location_key,
    to_char(d.order_date::date, 'YYYYMMDD')::int as date_key,
    d.carrier,
    d.shipment_date,
    d.delivery_date,
    d.promised_delivery_date,
    d.delivery_status,
    d.order_to_ship_days,
    d.ship_to_delivery_days,
    d.total_delivery_days,
    case when d.on_time_flag then 1 when d.on_time_flag is false then 0 else null end as on_time_flag,
    d.is_delayed
from {{ ref('int_delivery_metrics') }} d
where d.shipment_id is not null
