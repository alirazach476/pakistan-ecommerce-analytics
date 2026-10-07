with source as (
    select * from {{ source('raw', 'payments') }}
)

select
    payment_id,
    order_id,
    payment_method,
    payment_status,
    payment_amount::numeric(14, 2) as payment_amount,
    payment_date::timestamp as payment_date,
    payment_date::date as payment_date_day,
    transaction_ref,
    created_at,
    loaded_at,
    source_file
from source
where payment_amount >= 0
