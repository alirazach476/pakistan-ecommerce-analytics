"""
Airflow DAG: Pakistan E-commerce Analytics Platform

Flow:
  Generate / Ingest Data
        ↓
  Validate Raw Data
        ↓
  Load PostgreSQL
        ↓
  Run dbt
        ↓
  Run Data Quality Checks
        ↓
  Generate Analytics Exports
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

REPO_CANDIDATE = Path(__file__).resolve().parents[2]
if (REPO_CANDIDATE / "src").exists():
    PROJECT_ROOT = str(REPO_CANDIDATE)
else:
    PROJECT_ROOT = os.environ.get("AIRFLOW_PROJ_DIR", "/opt/airflow/project")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _generate_data() -> None:
    from src.data_generation.generate import generate_all

    generate_all()


def _validate_raw() -> None:
    from src.validation.validate_raw import validate_raw_directory

    summary = validate_raw_directory()
    if not summary["ok"]:
        raise ValueError("Raw validation failed")


def _load_postgres() -> None:
    from src.ingestion.pipeline import run_pipeline

    run_pipeline()


def _export_excel() -> None:
    from src.transformation.export_excel import export_summaries

    export_summaries()


def _generate_insights() -> None:
    from src.transformation.generate_insights import generate_insights

    generate_insights()


with DAG(
    dag_id="pakistan_ecommerce_analytics",
    description="End-to-end Pakistani e-commerce analytics pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["pakistan", "ecommerce", "analytics", "dbt"],
) as dag:
    generate = PythonOperator(
        task_id="generate_ingest_data",
        python_callable=_generate_data,
    )

    validate = PythonOperator(
        task_id="validate_raw_data",
        python_callable=_validate_raw,
    )

    load = PythonOperator(
        task_id="load_postgresql",
        python_callable=_load_postgres,
    )

    dbt_dir = os.path.join(PROJECT_ROOT, "dbt")
    dbt_run = BashOperator(
        task_id="run_dbt",
        bash_command=f"cd {dbt_dir} && dbt run --profiles-dir .",
        env={**os.environ, "POSTGRES_HOST": os.environ.get("POSTGRES_HOST", "postgres")},
    )

    dbt_test = BashOperator(
        task_id="run_data_quality_checks",
        bash_command=f"cd {dbt_dir} && dbt test --profiles-dir .",
        env={**os.environ, "POSTGRES_HOST": os.environ.get("POSTGRES_HOST", "postgres")},
    )

    analytics_exports = PythonOperator(
        task_id="generate_analytics_tables",
        python_callable=_export_excel,
    )

    insights = PythonOperator(
        task_id="generate_business_insights",
        python_callable=_generate_insights,
    )

    generate >> validate >> load >> dbt_run >> dbt_test >> analytics_exports >> insights
