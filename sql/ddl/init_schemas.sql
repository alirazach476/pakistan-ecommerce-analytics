-- Initialize warehouse schemas for Pakistan E-commerce Analytics Platform
-- Runs automatically on first PostgreSQL container start.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS ops;

COMMENT ON SCHEMA raw IS 'Landing zone for ingested source data (append/replace loads)';
COMMENT ON SCHEMA staging IS 'dbt staging models — cleaned, typed, renamed';
COMMENT ON SCHEMA intermediate IS 'dbt intermediate models — business logic building blocks';
COMMENT ON SCHEMA analytics IS 'Star-schema marts for BI tools (Power BI)';
COMMENT ON SCHEMA ops IS 'Pipeline monitoring, run logs, and operational metadata';

GRANT USAGE ON SCHEMA raw TO PUBLIC;
GRANT USAGE ON SCHEMA staging TO PUBLIC;
GRANT USAGE ON SCHEMA intermediate TO PUBLIC;
GRANT USAGE ON SCHEMA analytics TO PUBLIC;
GRANT USAGE ON SCHEMA ops TO PUBLIC;
