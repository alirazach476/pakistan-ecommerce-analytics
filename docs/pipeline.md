# Pipeline Documentation

## Stages

1. **Generate** — `python -m src.data_generation.generate`  
   Writes CSV files to `data/raw/` plus `generation_metadata.json`.

2. **Validate** — `python -m src.validation.validate_raw`  
   Checks schema, nulls, duplicates, accepted values, FK integrity, business rules.  
   Report: `data/processed/validation_report.json`.

3. **Load** — `python -m src.ingestion.pipeline`  
   Extract → validate → transform (types/audit cols) → PostgreSQL `raw` via `COPY`.  
   Ops logging in `ops.pipeline_runs` and `ops.data_freshness`.

4. **Transform (dbt)** — `dbt run` / `dbt test`  
   Builds staging, intermediate, and analytics marts.

5. **Export / Insights** — Excel summaries + `analysis/business_insights.md`.

## Airflow

DAG id: `pakistan_ecommerce_analytics`  
File: `airflow/dags/pakistan_ecommerce_pipeline.py`

Task chain matches the stages above.

## Logging

Structured logs go to console and `logs/pipeline.log` with messages such as:

- Pipeline started
- Files discovered / Rows read
- Rows validated / rejected
- Rows inserted
- Transformation started/completed
- Pipeline completed
