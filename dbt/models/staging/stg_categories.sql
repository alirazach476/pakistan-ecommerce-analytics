with source as (
    select * from {{ source('raw', 'categories') }}
)

select
    category_id,
    category_name,
    parent_category,
    loaded_at,
    source_file
from source
