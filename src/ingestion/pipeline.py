"""End-to-end ingestion pipeline: extract → validate → transform → load."""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone

from src.ingestion.extract import extract_all
from src.ingestion.load import (
    ensure_schema,
    finish_pipeline_run,
    load_all,
    start_pipeline_run,
)
from src.ingestion.transform import transform_all
from src.ingestion.validate import validate_datasets
from src.utils.config import get_settings
from src.utils.db import get_engine
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def run_pipeline() -> dict:
    """Execute the full raw-layer ingestion pipeline."""
    settings = get_settings()
    settings.logs_path.mkdir(parents=True, exist_ok=True)
    settings.processed_path.mkdir(parents=True, exist_ok=True)

    logger.info("Pipeline started — ingestion ETL")
    engine = get_engine()
    ensure_schema(engine)
    run_id = start_pipeline_run(engine, "raw_ingestion")

    rows_processed = 0
    rows_failed = 0
    summary: dict = {"pipeline_run_id": run_id}

    try:
        datasets = extract_all()
        if not datasets:
            raise FileNotFoundError(
                f"No raw CSV files found in {settings.raw_path}. Run data generation first."
            )

        validation = validate_datasets(datasets)
        summary["validation"] = validation
        if not validation["ok"]:
            raise ValueError("Raw data validation failed. See logs and validation details.")

        transformed = transform_all(datasets)
        counts = load_all(transformed, recreate_schema=True)
        rows_processed = sum(counts.values())
        summary["row_counts"] = counts
        summary["status"] = "success"
        summary["completed_at"] = datetime.now(timezone.utc).isoformat()

        finish_pipeline_run(
            engine,
            run_id,
            status="success",
            rows_processed=rows_processed,
            rows_failed=0,
            metadata={"row_counts": counts},
        )
        logger.info("Rows inserted (total): %s", f"{rows_processed:,}")
        logger.info("Pipeline completed — ingestion ETL")

    except Exception as exc:
        rows_failed = 1
        summary["status"] = "failed"
        summary["error"] = str(exc)
        logger.error("Pipeline failed: %s", exc)
        logger.error(traceback.format_exc())
        finish_pipeline_run(
            engine,
            run_id,
            status="failed",
            rows_processed=rows_processed,
            rows_failed=rows_failed,
            error_message=str(exc),
        )
        engine.dispose()
        raise
    finally:
        report_path = settings.processed_path / "ingestion_summary.json"
        report_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        logger.info("Summary report written to %s", report_path)

    engine.dispose()
    return summary


def main() -> None:
    summary = run_pipeline()
    print("\nIngestion summary:")
    print(json.dumps(summary.get("row_counts", {}), indent=2))


if __name__ == "__main__":
    main()
