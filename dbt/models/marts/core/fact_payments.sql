-- Grain: one row per payment
with payments as (
    select * from {{ ref('stg_payments') }}
),

methods as (
    select * from {{ ref('dim_payment_method') }}
)

select
    p.payment_id as payment_key,
    p.payment_id,
    p.order_id as order_key,
    m.payment_method_key,
    p.payment_method,
    p.payment_status,
    p.payment_amount,
    p.payment_date,
    to_char(p.payment_date_day, 'YYYYMMDD')::int as date_key,
    case when p.payment_status = 'Paid' then 1 else 0 end as is_successful,
    case when p.payment_status = 'Failed' then 1 else 0 end as is_failed,
    case when p.payment_status = 'Refunded' then 1 else 0 end as is_refunded,
    p.transaction_ref
from payments p
left join methods m on p.payment_method = m.payment_method
