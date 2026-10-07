"""Load transformed datasets into PostgreSQL raw schema."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.ingestion.extract import TABLE_ORDER
from src.utils.config import get_settings
from src.utils.db import execute_sql_file, get_engine, table_row_count
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

TRUNCATE_ORDER = list(reversed(TABLE_ORDER))


def ensure_schema(engine: Engine) -> None:
    execute_sql_file(engine, "sql/ddl/init_schemas.sql")
    execute_sql_file(engine, "sql/ddl/raw_tables.sql")
    logger.info("Raw schema and tables ensured")


def start_pipeline_run(engine: Engine, pipeline_name: str) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                INSERT INTO ops.pipeline_runs (pipeline_name, start_time, status)
                VALUES (:name, :start, 'running')
                RETURNING pipeline_run_id
                """
            ),
            {"name": pipeline_name, "start": datetime.now(timezone.utc)},
        )
        run_id = int(result.scalar_one())
    logger.info("Started pipeline_run_id=%s", run_id)
    return run_id


def finish_pipeline_run(
    engine: Engine,
    run_id: int,
    status: str,
    rows_processed: int,
    rows_failed: int,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE ops.pipeline_runs
                SET end_time = :end,
                    status = :status,
                    rows_processed = :rows_processed,
                    rows_failed = :rows_failed,
                    error_message = :error_message,
                    metadata = CAST(:metadata AS jsonb)
                WHERE pipeline_run_id = :run_id
                """
            ),
            {
                "end": datetime.now(timezone.utc),
                "status": status,
                "rows_processed": rows_processed,
                "rows_failed": rows_failed,
                "error_message": error_message,
                "metadata": json.dumps(metadata or {}),
                "run_id": run_id,
            },
        )


def update_freshness(
    engine: Engine, table: str, row_count: int, source_file: str
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO ops.data_freshness (table_name, last_successful_load, row_count, source_file, updated_at)
                VALUES (:table_name, :loaded, :row_count, :source_file, :updated)
                ON CONFLICT (table_name) DO UPDATE
                SET last_successful_load = EXCLUDED.last_successful_load,
                    row_count = EXCLUDED.row_count,
                    source_file = EXCLUDED.source_file,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "table_name": f"raw.{table}",
                "loaded": datetime.now(timezone.utc),
                "row_count": row_count,
                "source_file": source_file,
                "updated": datetime.now(timezone.utc),
            },
        )


def truncate_raw(engine: Engine) -> None:
    with engine.begin() as conn:
        for table in TRUNCATE_ORDER:
            conn.execute(text(f'TRUNCATE TABLE raw."{table}" CASCADE'))
            logger.info("Truncated raw.%s", table)


def _copy_dataframe(engine: Engine, df: pd.DataFrame, schema: str, table: str) -> int:
    """High-performance load using PostgreSQL COPY."""
    if df.empty:
        return 0

    columns = list(df.columns)
    col_list = ", ".join(f'"{c}"' for c in columns)
    buffer = io.StringIO()
    # Normalize values for CSV COPY
    export_df = df.copy()
    for col in export_df.columns:
        if pd.api.types.is_datetime64_any_dtype(export_df[col]):
            export_df[col] = pd.to_datetime(export_df[col], errors="coerce").dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        elif pd.api.types.is_bool_dtype(export_df[col]):
            export_df[col] = export_df[col].map({True: "true", False: "false"})
        elif export_df[col].dtype == object:
            # Normalize Python bools mixed in object columns
            export_df[col] = export_df[col].map(
                lambda v: ("true" if v is True else "false" if v is False else v)
            )
        export_df[col] = export_df[col].where(pd.notnull(export_df[col]), None)

    export_df.to_csv(buffer, index=False, header=False, na_rep="\\N", quoting=csv.QUOTE_MINIMAL)
    buffer.seek(0)

    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            cur.copy_expert(
                f'COPY "{schema}"."{table}" ({col_list}) FROM STDIN WITH (FORMAT CSV, NULL \'\\N\')',
                buffer,
            )
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()
    return len(df)


def load_table(engine: Engine, name: str, df: pd.DataFrame) -> int:
    # Keep only columns that exist on the target table
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'raw' AND table_name = :table
                ORDER BY ordinal_position
                """
            ),
            {"table": name},
        )
        db_cols = [row[0] for row in result]

    usable = [c for c in df.columns if c in db_cols]
    missing_required = [c for c in db_cols if c not in usable and c not in ("created_at", "updated_at")]
    # created_at/updated_at have defaults; optional
    subset = df[usable].copy()
    inserted = _copy_dataframe(engine, subset, schema="raw", table=name)
    update_freshness(engine, name, inserted, f"{name}.csv")
    logger.info("Rows inserted into raw.%s: %s", name, f"{inserted:,}")
    if missing_required:
        logger.debug("Columns using DB defaults or skipped: %s", missing_required)
    return inserted


def load_all(datasets: dict[str, pd.DataFrame], recreate_schema: bool = True) -> dict[str, int]:
    engine = get_engine()
    if recreate_schema:
        ensure_schema(engine)
        truncate_raw(engine)

    counts: dict[str, int] = {}
    for name in TABLE_ORDER:
        if name not in datasets:
            logger.warning("Skipping missing dataset: %s", name)
            continue
        counts[name] = load_table(engine, name, datasets[name])

    for name, expected in counts.items():
        actual = table_row_count(engine, "raw", name)
        logger.info("Verify raw.%s count=%s (loaded=%s)", name, f"{actual:,}", f"{expected:,}")
        if actual != expected:
            raise RuntimeError(f"Row count mismatch for raw.{name}: db={actual} loaded={expected}")

    engine.dispose()
    return counts
