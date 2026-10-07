# Architecture Decision Records (ADRs)

## ADR-001: Why PostgreSQL?

**Decision:** Use PostgreSQL 16 as the analytical warehouse for this portfolio project.

**Rationale:**
- Free, widely used, and easy to run in Docker
- Strong SQL support for window functions, CTEs, and constraints
- First-class dbt-postgres adapter
- Sufficient for ~1M fact rows on a laptop

**Alternatives considered:** SQLite (too limited for BI concurrency), DuckDB (excellent locally but less common in enterprise interview stories for classic warehouses).

---

## ADR-002: Why star schema?

**Decision:** Model the `analytics` schema as a dimensional star schema.

**Rationale:**
- Matches Power BI / tabular model best practices
- Clear grain on facts simplifies KPI definitions
- Dimensions are reusable across multiple facts

---

## ADR-003: Why dbt?

**Decision:** Use dbt Core for transformations after raw load.

**Rationale:**
- Version-controlled SQL models
- Built-in tests (`unique`, `not_null`, `relationships`, `accepted_values`)
- Documentation and lineage
- Industry-standard Analytics Engineering skill signal

---

## ADR-004: Why Airflow?

**Decision:** Provide an Airflow DAG that mirrors the pipeline stages.

**Rationale:**
- Demonstrates orchestration beyond “run scripts manually”
- Clear task dependencies for interview discussion
- Optional profile in Docker Compose so core demo can run without Airflow

---

## ADR-005: Why synthetic data?

**Decision:** Generate synthetic Pakistani e-commerce data instead of using proprietary dumps.

**Rationale:**
- Real marketplace datasets are not publicly shareable
- Full control over referential integrity and edge cases
- Reproducible via `RANDOM_SEED`

**Constraint:** Documentation must clearly label data as synthetic.

---

## ADR-006: Why batch processing?

**Decision:** Use batch ETL/ELT rather than streaming.

**Rationale:**
- Matches daily/hourly analytics refresh patterns common for e-commerce BI
- Simpler to operate and test in a portfolio environment
- Streaming (Kafka → Flink) is documented as a future scale path, not a v1 requirement

---

## ADR-007: Fact table grains

| Fact | Grain |
|------|-------|
| `fact_orders` | One row per order |
| `fact_order_items` | One row per order item |
| `fact_payments` | One row per payment transaction |
| `fact_shipments` | One row per shipment (1:1 with order in this dataset) |
| `fact_returns` | One row per return |

---

## ADR-008: KPI definitions

**Decision:** Publish explicit formulas for Gross Revenue, Net Revenue, AOV, Return Rate, CLV, etc. in `docs/business_metrics.md`.

**Rationale:** Ambiguous KPIs cause conflicting dashboards. Interviewers often ask “how did you define revenue?”

---

## ADR-009: Validation approach

**Decision:** Implement lightweight Python validation (schema, nulls, duplicates, FK, accepted values, business rules) plus dbt tests. Great Expectations is listed as optional/extended quality.

**Rationale:** Keeps the core pipeline runnable with fewer moving parts while still demonstrating quality engineering.
