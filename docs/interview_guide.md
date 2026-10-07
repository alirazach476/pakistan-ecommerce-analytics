# Interview Guide

Concise answers for portfolio interviews.

### What did you build?

An end-to-end Pakistan e-commerce analytics platform: synthetic data generation, Python ETL with validation, PostgreSQL layered warehouse, dbt transformations to a star schema, Airflow orchestration, Power BI-ready marts, KPI documentation, and business insights generated from actual SQL results.

### What was the architecture?

Batch ELT: landing CSVs → validate/load to `raw` → dbt staging/intermediate/marts in PostgreSQL → Power BI on `analytics` facts/dimensions. Airflow DAG orchestrates the stages.

### Why did you use PostgreSQL?

Open source, strong SQL, easy Docker setup, excellent dbt support, and realistic for junior DE interviews without cloud cost.

### Why star schema?

BI tools work best with facts (measures at a declared grain) and dimensions (descriptive attributes). It simplifies DAX and avoids wide, report-specific flat tables.

### What is ETL?

Extract data from sources, Transform it (clean/types/rules), Load into a target. In this project the Python path validates and lightly transforms before load.

### What is ELT?

Load raw data first, then Transform in the warehouse (dbt SQL). This project is primarily ELT after the raw load.

### Why dbt?

Version-controlled SQL models, tests, docs, and clear layering (staging → intermediate → marts) — standard Analytics Engineering practice.

### Why Airflow?

To express dependencies and schedule the pipeline as a DAG rather than a pile of manual scripts.

### What is a fact table?

A table of measurable events at a specific grain (e.g., sales amounts, quantities, flags).

### What is a dimension table?

Descriptive context for slicing facts (customer, product, date, location).

### What is the grain of fact_order_items?

One row per order item (line).

### How did you handle data quality?

Python pre-load checks (nulls, duplicates, FKs, accepted values, business rules) plus dbt tests (`unique`, `not_null`, `relationships`, `accepted_values`, singular SQL tests).

### How did you handle duplicate records?

Primary-key uniqueness checks reject duplicate IDs before load; dbt `unique` tests guard marts.

### How did you handle missing data?

Required fields fail validation; optional fields remain null; monetary fields coerced carefully; invalid quantities filtered in transform.

### How did you calculate revenue?

Gross = quantity × unit_price; Net = gross − discounts − refunds (documented in `docs/business_metrics.md`).

### How did you calculate customer lifetime value?

Historical net revenue per customer (portfolio proxy, not a predictive LTV model).

### How does Power BI connect to the warehouse?

DirectQuery or Import from PostgreSQL `analytics` schema using star-schema relationships documented in `dashboards/powerbi/data_model.md`.

### How would you scale this to 10 million orders?

- Parquet/object storage landing
- COPY/parallel loads, partitioning by date
- Incremental dbt models
- Heavier warehouse (Redshift/BigQuery/Synapse)
- Orchestration alerts & data contracts

### How would you move this to AWS/Azure/GCP?

Land files in S3/ADLS/GCS → Glue/ADF/Dataflow → Redshift/Synapse/BigQuery → dbt → Power BI. Same logical architecture, managed services for scale.
