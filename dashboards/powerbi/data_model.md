# Power BI Data Model

Connect Power BI Desktop to PostgreSQL and import tables from the `analytics` schema.

## Connection

| Setting | Value |
|---------|-------|
| Server | `localhost` (or Docker host) |
| Database | `pakistan_ecommerce` |
| Schema | `analytics` |
| Auth | Database credentials from `.env` |

## Tables to import

### Facts

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_shipments`
- `fact_returns`

### Dimensions

- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_seller`
- `dim_category`
- `dim_location`
- `dim_payment_method`
- `dim_order_status`

### Optional aggregates

- `fct_daily_revenue`
- `fct_customer_rfm`
- `fct_location_performance`

## Relationships

Prefer single-direction filters from dimensions → facts.

| From (1) | To (*) | Key |
|----------|--------|-----|
| dim_date | fact_orders | date_key |
| dim_date | fact_order_items | date_key |
| dim_date | fact_payments | date_key |
| dim_date | fact_shipments | date_key |
| dim_date | fact_returns | date_key |
| dim_customer | fact_orders | customer_key |
| dim_customer | fact_order_items | customer_key |
| dim_product | fact_order_items | product_key |
| dim_seller | fact_order_items | seller_key |
| dim_location | fact_orders | location_key |
| dim_payment_method | fact_payments | payment_method_key |
| dim_order_status | fact_orders | order_status_key |
| dim_category | dim_product | category_id / category_key |

Mark `dim_date[full_date]` as the Date table for time intelligence.

## Modeling rules

- Avoid many-to-many relationships
- Do not relate multiple facts directly to each other; use shared dimensions (conformed dimensions)
- Prefer measures over calculated columns for rates and ratios
