{{ config(materialized='table') }}

with bounds as (
    select
        min(order_date_day) as start_date,
        max(order_date_day) as end_date
    from {{ ref('stg_orders') }}
),

spine as (
    select
        generate_series(
            (select start_date from bounds),
            (select end_date from bounds),
            interval '1 day'
        )::date as full_date
)

select
    to_char(full_date, 'YYYYMMDD')::int as date_key,
    full_date,
    extract(day from full_date)::int as day,
    to_char(full_date, 'Day') as day_name,
    extract(week from full_date)::int as week,
    extract(month from full_date)::int as month,
    to_char(full_date, 'Month') as month_name,
    extract(quarter from full_date)::int as quarter,
    extract(year from full_date)::int as year,
    case when extract(dow from full_date) in (0, 6) then true else false end as is_weekend,
    date_trunc('month', full_date)::date as month_start,
    (date_trunc('month', full_date) + interval '1 month - 1 day')::date as month_end
from spine
