# Pakistan E-commerce Analytics Platform

End-to-end analytics platform for a **fictional Pakistani e-commerce marketplace**, built as a portfolio project for Data Engineer, Analytics Engineer, Data Analyst, and BI roles.

This is **not** a simple CSV → Power BI demo. It implements a reproducible pipeline:

**Raw Data → Validation → ETL → PostgreSQL → dbt → Analytics Marts → Power BI-ready datasets → Insights → Tests → Docker**

---

## Dataset disclaimer

> **This project uses synthetic data generated to simulate a Pakistani e-commerce marketplace. It is intended for demonstrating data engineering and analytics skills and does not represent actual company data.**

---

## Business problem

Marketplace operators in Pakistan need a trustworthy analytics foundation to answer questions about revenue, customers, sellers, logistics, payments, and returns — with clear KPI definitions, quality controls, and a BI-ready star schema.

## Objectives

- Generate realistic, relational synthetic e-commerce data (PKR, Pakistani cities/provinces)
- Ingest and validate data into a layered PostgreSQL warehouse
- Transform with dbt (staging → intermediate → marts)
- Expose analytics tables for Power BI
- Document KPIs, architecture decisions, and interview talking points

## Architecture

```text
Synthetic Data (Python)
        ↓
   data/raw (CSV)
        ↓
 Python ETL (validate + load)
        ↓
 PostgreSQL raw schema
        ↓
 dbt (staging / intermediate / marts)
        ↓
 analytics star schema
        ↓
 Power BI + Excel exports + business insights
```

Orchestration is modeled in Apache Airflow (`airflow/dags`).

See [docs/architecture.md](docs/architecture.md) for diagrams and design rationale.

## Technology stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Database | PostgreSQL 16 |
| Transforms | dbt Core + dbt-postgres |
| Orchestration | Apache Airflow 2.10 |
| Validation | Custom rules + pytest |
| BI | Power BI (model + DAX specs) |
| Infra | Docker Compose |

## Project structure

```text
├── src/data_generation/   # Synthetic Pakistani e-commerce data
├── src/ingestion/         # Extract → validate → transform → load
├── src/validation/        # Raw data quality checks
├── src/transformation/    # Exports & insight generation
├── sql/ddl/               # Warehouse DDL
├── dbt/                   # Staging, intermediate, marts
├── airflow/dags/          # Pipeline DAG
├── dashboards/powerbi/    # Model, DAX, dashboard specs
├── analysis/              # Business insights from real queries
├── docs/                  # Architecture, dictionary, interview guide
└── tests/                 # pytest suite
```

## Results (verified local run)

| Check | Result |
|-------|--------|
| Synthetic data generation | Customers 100k · Orders 300k · Order items **901,205** · Returns 30k |
| Raw load | **1,937,248** rows into PostgreSQL `raw` |
| dbt run | **30/30** models |
| dbt test | **64/64** passed |
| pytest | **8/8** passed |
| Gross / Net revenue (synthetic) | PKR 121.79B / PKR 113.38B |

Insights file: [analysis/business_insights.md](analysis/business_insights.md)

## Live Dashboard (Vercel)

**https://pakistanecommerce.vercel.app**

6-page interactive BI dashboard (Executive, Sales, Customers, Products & Sellers, Logistics, Returns & Payments) built with Next.js + Recharts. Data is exported from the PostgreSQL `analytics` schema to static JSON for Vercel hosting.

To refresh dashboard data after re-running the pipeline:

```powershell
python scripts/export_dashboard_json.py
cd web && npx vercel deploy --prod
```

## How to run

### Prerequisites

- Python 3.11+
- Docker Desktop **or** `embedded-postgres` (fallback when Docker is unavailable)
- Make (optional; PowerShell equivalents below)

### 1. Setup

```bash
cp .env.example .env
# Edit POSTGRES_PASSWORD and related values
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
# Optional fallback DB (no Docker):
pip install embedded-postgres
```

### 2. Start PostgreSQL

**Preferred (Docker):**

```bash
docker compose up -d postgres
```

**Fallback (no Docker):**

```bash
# Windows PowerShell
$env:PYTHONPATH = (Get-Location).Path
python scripts/start_embedded_postgres.py
# Loads env vars from updated .env (host/port)
Get-Content .env | ForEach-Object {
  if ($_ -match '=' -and $_ -notmatch '^\s*#') {
    $k,$v = $_.Split('=',2); Set-Item "Env:$($k.Trim())" $v.Trim()
  }
}
```

### 3. Generate → validate → load → dbt

```bash
# With Make
make generate-data
make validate
make load
make dbt-run
make dbt-test

# Or full pipeline
make pipeline
```

**Windows PowerShell (without Make):**

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m src.data_generation.generate
python -m src.validation.validate_raw
python -m src.ingestion.pipeline
cd dbt; dbt run --profiles-dir .; dbt test --profiles-dir .; cd ..
python -m src.transformation.export_excel
python -m src.transformation.generate_insights
pytest tests/ -v
```

Or run `scripts/run_pipeline.ps1` after PostgreSQL is up.

### 4. Airflow (optional)

```bash
docker compose --profile airflow up -d
# UI: http://localhost:8080  (admin / value from .env)
```

### 5. Power BI

Connect Power BI Desktop to PostgreSQL (`analytics` schema).  
Follow [dashboards/powerbi/data_model.md](dashboards/powerbi/data_model.md) and [dashboards/powerbi/dax_measures.md](dashboards/powerbi/dax_measures.md).

## Target dataset scale

| Entity | Target rows |
|--------|-------------|
| Customers | 100,000 |
| Products | 5,000 |
| Sellers | 1,000 |
| Orders | 300,000 |
| Order items | 500,000+ |
| Payments | 300,000 |
| Shipments | 300,000 |
| Returns | 30,000+ |

## Data model (star schema)

**Dimensions:** `dim_customer`, `dim_product`, `dim_seller`, `dim_category`, `dim_location`, `dim_date`, `dim_payment_method`, `dim_order_status`

**Facts:** `fact_orders`, `fact_order_items`, `fact_payments`, `fact_shipments`, `fact_returns`

Example grain: `fact_order_items` = **one row per order item**.

## KPIs (selected)

Total / Net Revenue · AOV · Return Rate · Cancellation Rate · Active / Repeat Customers · CLV · On-Time Delivery Rate · RFM segments

Definitions: [docs/business_metrics.md](docs/business_metrics.md)

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/architecture.md](docs/architecture.md) | Platform architecture |
| [docs/architecture_decisions.md](docs/architecture_decisions.md) | ADRs |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Column-level dictionary |
| [docs/pipeline.md](docs/pipeline.md) | ETL / orchestration |
| [docs/warehouse_design.md](docs/warehouse_design.md) | Schemas & grains |
| [docs/business_metrics.md](docs/business_metrics.md) | KPI definitions |
| [docs/interview_guide.md](docs/interview_guide.md) | Interview Q&A |
| [docs/final_report.md](docs/final_report.md) | End-of-project report |
| [analysis/business_insights.md](analysis/business_insights.md) | Insights from loaded data |

## Testing

```bash
pytest tests/ -v
cd dbt && dbt test --profiles-dir .
```

## Security

- Credentials via `.env` (never committed)
- `.env.example` provided as a template
- Synthetic personal data only (`@example.pk` emails)

## License

MIT — see [LICENSE](LICENSE)

## Future improvements

- Cloud deployment (S3/GCS + Glue/Dataflow + Redshift/BigQuery)
- Incremental dbt models for orders
- SCD Type 2 for sellers
- Great Expectations checkpoint suite in CI
