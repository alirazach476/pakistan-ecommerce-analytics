"""Ingestion-time validation wrappers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.logging_config import setup_logging
from src.validation.validate_raw import validate_table

logger = setup_logging(__name__)


def validate_datasets(datasets: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Validate in-memory datasets prior to load."""
    reports = {}
    all_ok = True
    for name, df in datasets.items():
        report = validate_table(name, df, datasets)
        reports[name] = {
            "ok": report.ok,
            "rows_read": report.rows_read,
            "rows_valid": report.rows_valid,
            "rows_rejected": report.rows_rejected,
            "errors": report.errors,
        }
        if report.ok:
            logger.info("Rows validated: %s (%s)", name, f"{report.rows_valid:,}")
        else:
            all_ok = False
            for err in report.errors:
                logger.error("Validation error [%s]: %s", name, err)
    return {"ok": all_ok, "tables": reports}
