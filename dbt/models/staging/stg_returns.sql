with source as (
    select * from {{ source('raw', 'returns') }}
)

select
    return_id,
    order_id,
    order_item_id,
    return_date::timestamp as return_date,
    return_date::date as return_date_day,
    return_reason,
    refund_amount::numeric(14, 2) as refund_amount,
    return_status,
    created_at,
    loaded_at,
    source_file
from source
where refund_amount >= 0
