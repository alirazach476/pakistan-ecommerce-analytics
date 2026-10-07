with source as (
    select * from {{ source('raw', 'shipments') }}
)

select
    shipment_id,
    order_id,
    carrier,
    shipment_date::timestamp as shipment_date,
    delivery_date::timestamp as delivery_date,
    promised_delivery_date::date as promised_delivery_date,
    delivery_status,
    tracking_number,
    case
        when shipment_date is not null and delivery_date is not null
            then extract(epoch from (delivery_date - shipment_date)) / 86400.0
        else null
    end as ship_to_delivery_days,
    created_at,
    loaded_at,
    source_file
from source
