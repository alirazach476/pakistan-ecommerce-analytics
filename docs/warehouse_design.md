# Warehouse Design

## Schemas

| Schema | Role |
|--------|------|
| `raw` | Landing tables, 1:1 with source files + audit columns |
| `staging` | dbt cleaned/typed models |
| `intermediate` | dbt business building blocks |
| `analytics` | Star schema marts for BI |
| `ops` | Pipeline runs & freshness |

## ER (conceptual)

```mermaid
erDiagram
    dim_customer ||--o{ fact_orders : places
    dim_location ||--o{ fact_orders : ships_to
    dim_date ||--o{ fact_orders : on
    dim_order_status ||--o{ fact_orders : has
    fact_orders ||--|{ fact_order_items : contains
    dim_product ||--o{ fact_order_items : includes
    dim_seller ||--o{ fact_order_items : fulfills
    fact_orders ||--o| fact_payments : paid_by
    fact_orders ||--o| fact_shipments : shipped_as
    fact_order_items ||--o{ fact_returns : returned_as
```

## Fact grains

| Fact | Grain |
|------|-------|
| fact_orders | one row per order |
| fact_order_items | one row per order item |
| fact_payments | one row per payment |
| fact_shipments | one row per shipment |
| fact_returns | one row per return |

## Indexes (raw layer)

Indexes on foreign keys and common filters (`order_date`, `order_status`, `payment_method`) are defined in `sql/ddl/raw_tables.sql` to speed loads and ad-hoc checks.

## SCD note

Current dimensions are Type 1 (overwrite). SCD Type 2 for sellers/customers is a documented future enhancement (`docs/final_report.md`).
