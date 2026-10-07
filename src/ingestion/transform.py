"""Light transforms before loading into the raw schema."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

DATETIME_COLUMNS: dict[str, list[str]] = {
    "sellers": ["registration_date"],
    "customers": ["birth_date", "registration_date"],
    "orders": ["order_date"],
    "payments": ["payment_date"],
    "shipments": ["shipment_date", "delivery_date", "promised_delivery_date"],
    "returns": ["return_date"],
}

BOOL_COLUMNS: dict[str, list[str]] = {
    "sellers": ["is_active"],
    "customers": ["is_active"],
    "products": ["is_active"],
}


def _parse_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            # Convert NaT to None for SQL NULL
            df[col] = df[col].astype(object).where(df[col].notna(), None)
    return df


def transform_table(name: str, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    logger.info("Transformation started: %s", name)
    out = df.copy()

    for col in BOOL_COLUMNS.get(name, []):
        if col in out.columns:
            out[col] = out[col].astype(bool)

    out = _parse_dates(out, DATETIME_COLUMNS.get(name, []))

    # Numeric cleanup
    money_cols = [
        c
        for c in out.columns
        if c.endswith("_amount")
        or c.endswith("_price")
        or c.endswith("_fee")
        or c in ("unit_price", "cost_price", "line_total", "total_amount", "payment_amount", "refund_amount")
    ]
    for col in money_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    if "quantity" in out.columns:
        out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
        out = out[out["quantity"] > 0]

    loaded_at = datetime.now(timezone.utc)
    out["loaded_at"] = loaded_at
    out["source_file"] = source_file

    # Align with raw DDL columns (drop generator-only helpers if present)
    drop_cols = [c for c in ("min_price_pkr", "max_price_pkr") if c in out.columns]
    if drop_cols:
        out = out.drop(columns=drop_cols)

    logger.info("Transformation completed: %s (%s rows)", name, f"{len(out):,}")
    return out


def transform_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    transformed: dict[str, pd.DataFrame] = {}
    for name, df in datasets.items():
        transformed[name] = transform_table(name, df, source_file=f"{name}.csv")
    return transformed
