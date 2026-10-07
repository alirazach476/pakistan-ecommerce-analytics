# Final Report — Pakistan E-commerce Analytics Platform

## 1. Project summary

Built a reproducible, end-to-end analytics platform for a **fictional Pakistani e-commerce marketplace**. The stack covers synthetic data generation, Python ETL with validation, PostgreSQL layered warehouse, dbt star-schema marts, Airflow orchestration, Power BI specs/DAX, Excel exports, pytest, and business insights computed from the live warehouse.

> This project uses **synthetic** data. It does **not** represent actual company data.

## 2. Architecture

```text
Synthetic CSV → Validate → Load raw.* → dbt (staging/intermediate/analytics) → Power BI / Excel / Insights
                              ↑
                         Airflow DAG
```

Details: [architecture.md](architecture.md), [architecture_decisions.md](architecture_decisions.md).

## 3. Dataset statistics (verified run)

| Entity | Rows |
|--------|------|
| Locations | 28 |
| Categories | 15 |
| Sellers | 1,000 |
| Customers | 100,000 |
| Products | 5,000 |
| Orders | 300,000 |
| Order items | 901,205 |
| Payments | 300,000 |
| Shipments | 300,000 |
| Returns | 30,000 |
| **Total loaded (raw)** | **1,937,248** |

Date range: 2023-01-01 → 2025-12-31 · Currency: PKR · Seed: 42

## 4. Data engineering implementation

- Generator: `src/data_generation/` (vectorized NumPy/Pandas, relational integrity)
- ETL: `src/ingestion/` extract → validate → transform → PostgreSQL `COPY`
- Ops tables: `ops.pipeline_runs`, `ops.data_freshness`
- Audit columns: `loaded_at`, `source_file`

## 5. Warehouse design

Schemas: `raw`, `staging`, `intermediate`, `analytics`, `ops`  
Star schema facts/dims documented in [warehouse_design.md](warehouse_design.md).  
Grain example: `fact_order_items` = one row per order item.

## 6. Data quality

- Pre-load Python checks (schema, nulls, duplicates, FKs, accepted values, business rules)
- dbt: **64/64 tests passed** (unique, not_null, relationships, accepted_values, singular SQL tests)
- pytest: **8/8 passed**

## 7. dbt implementation

- 30 models built successfully (staging views, intermediate views, analytics tables)
- Custom `generate_schema_name` macro for clean schema names
- Sources defined on `raw.*`

## 8. Analytics

Verified warehouse KPIs (synthetic):

| Metric | Value |
|--------|------:|
| Gross revenue | PKR 121,793,639,155.27 |
| Net revenue | PKR 113,376,438,051.32 |
| AOV | PKR 387,810.60 |
| Cancellation rate | 7.09% |
| Return-related order rate | 10.00% |
| Customers with orders | 59,807 |

Top cities by revenue: **Karachi**, **Lahore**, **Faisalabad**.  
Top category by revenue: **Mobile Phones**.

Full narrative: [../analysis/business_insights.md](../analysis/business_insights.md).

## 9. KPI definitions

See [business_metrics.md](business_metrics.md). Gross = qty × unit_price; Net = gross − discounts − refunds. CLV = historical net revenue (not predictive).

## 10. Business insights

Generated from SQL against `analytics.*` — not fabricated. Answers cover city revenue, category returns, seller quality, monthly growth, repeat customers, payment mix, delivery friction, segments, and high-return products.

## 11. Dashboard design

Six-page Power BI specification + DAX measures in `dashboards/powerbi/`. Connect to PostgreSQL `analytics` schema.

## 12. Testing

| Suite | Result |
|-------|--------|
| pytest | 8 passed |
| dbt test | 64 passed |
| Airflow DAG | Python syntax validated |

## 13. Performance notes

- Vectorized generation (~22s for full synthetic set on this machine)
- PostgreSQL `COPY` for bulk load (~80s end-to-end ingest including transforms)
- dbt run ~18s for 30 models after raw load
- Indexes on raw FKs and common filters

## 14. Limitations

- Docker was not available in the build environment; local run used **embedded PostgreSQL** (`scripts/start_embedded_postgres.py`). Prefer Docker Compose when available.
- Dimensions are SCD Type 1 (overwrite), not Type 2
- CLV is historical, not predictive
- Power BI `.pbix` is specified, not shipped (binary); screenshots are placeholders
- Airflow profile not executed in this environment (DAG file validated)

## 15. Future improvements

- Incremental dbt models for orders
- SCD Type 2 for sellers
- Cloud landing (S3/ADLS/GCS) + managed warehouse
- CI pipeline (GitHub Actions) for pytest + dbt test
- Great Expectations checkpoints

## 16. Interview talking points

Use [interview_guide.md](interview_guide.md). Emphasize grain, KPI definitions, ELT vs ETL, dbt tests, and that insights were queried from the warehouse.
