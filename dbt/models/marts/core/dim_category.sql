select
    category_id as category_key,
    category_id,
    category_name,
    parent_category
from {{ ref('stg_categories') }}
