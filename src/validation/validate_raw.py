"""Validate synthetic raw CSV datasets before warehouse load."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from src.data_generation.constants import (
    ORDER_STATUSES,
    PAYMENT_METHODS,
    PAYMENT_STATUSES,
    RETURN_REASONS,
)
from src.utils.config import get_settings
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

REQUIRED_FILES = [
    "locations",
    "categories",
    "sellers",
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "shipments",
    "returns",
]

SCHEMAS: dict[str, list[str]] = {
    "locations": ["location_id", "city", "province", "region", "country"],
    "categories": ["category_id", "category_name"],
    "sellers": ["seller_id", "seller_name", "location_id", "registration_date"],
    "customers": ["customer_id", "first_name", "last_name", "email", "location_id"],
    "products": ["product_id", "product_name", "category_id", "seller_id", "unit_price"],
    "orders": ["order_id", "customer_id", "order_date", "order_status", "total_amount"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    "payments": ["payment_id", "order_id", "payment_method", "payment_status", "payment_amount"],
    "shipments": ["shipment_id", "order_id", "delivery_status"],
    "returns": ["return_id", "order_id", "order_item_id", "return_reason", "refund_amount"],
}


@dataclass
class ValidationReport:
    table: str
    rows_read: int = 0
    rows_valid: int = 0
    rows_rejected: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def validate_table(name: str, df: pd.DataFrame, datasets: dict[str, pd.DataFrame]) -> ValidationReport:
    report = ValidationReport(table=name, rows_read=len(df))
    required_cols = SCHEMAS[name]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report

    # Completeness / uniqueness on primary keys
    pk_map = {
        "locations": "location_id",
        "categories": "category_id",
        "sellers": "seller_id",
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id",
        "order_items": "order_item_id",
        "payments": "payment_id",
        "shipments": "shipment_id",
        "returns": "return_id",
    }
    pk = pk_map[name]
    null_pk = int(df[pk].isna().sum())
    if null_pk:
        report.errors.append(f"{pk} has {null_pk} null values")
    dup_pk = int(df[pk].duplicated().sum())
    if dup_pk:
        report.errors.append(f"{pk} has {dup_pk} duplicates")

    # Table-specific rules
    if name == "orders":
        invalid_status = ~df["order_status"].isin(ORDER_STATUSES)
        if invalid_status.any():
            report.errors.append(
                f"Invalid order_status values: {df.loc[invalid_status, 'order_status'].unique()[:5]}"
            )
        if (df["total_amount"] < 0).any():
            report.errors.append("total_amount contains negative values")
        missing_customers = ~df["customer_id"].isin(datasets["customers"]["customer_id"])
        if missing_customers.any():
            report.errors.append(
                f"{int(missing_customers.sum())} orders reference missing customers"
            )

    if name == "order_items":
        if (df["quantity"] <= 0).any():
            report.errors.append("quantity must be > 0")
        if (df["unit_price"] < 0).any():
            report.errors.append("unit_price must be >= 0")
        missing_products = ~df["product_id"].isin(datasets["products"]["product_id"])
        if missing_products.any():
            report.errors.append(
                f"{int(missing_products.sum())} order_items reference missing products"
            )
        missing_orders = ~df["order_id"].isin(datasets["orders"]["order_id"])
        if missing_orders.any():
            report.errors.append(
                f"{int(missing_orders.sum())} order_items reference missing orders"
            )

    if name == "payments":
        invalid_method = ~df["payment_method"].isin(PAYMENT_METHODS)
        if invalid_method.any():
            report.errors.append("Invalid payment_method values found")
        invalid_status = ~df["payment_status"].isin(PAYMENT_STATUSES)
        if invalid_status.any():
            report.errors.append("Invalid payment_status values found")

    if name == "products":
        if (df["unit_price"] < 0).any():
            report.errors.append("unit_price must be >= 0")
        missing_sellers = ~df["seller_id"].isin(datasets["sellers"]["seller_id"])
        if missing_sellers.any():
            report.errors.append(
                f"{int(missing_sellers.sum())} products reference missing sellers"
            )

    if name == "shipments":
        ship = pd.to_datetime(df["shipment_date"], errors="coerce")
        deliv = pd.to_datetime(df["delivery_date"], errors="coerce")
        bad = deliv.notna() & ship.notna() & (deliv < ship)
        if bad.any():
            report.errors.append(
                f"{int(bad.sum())} shipments have delivery_date < shipment_date"
            )

    if name == "returns":
        invalid_reason = ~df["return_reason"].isin(RETURN_REASONS)
        if invalid_reason.any():
            report.errors.append("Invalid return_reason values found")
        if (df["refund_amount"] < 0).any():
            report.errors.append("refund_amount must be >= 0")
        missing_items = ~df["order_item_id"].isin(datasets["order_items"]["order_item_id"])
        if missing_items.any():
            report.errors.append(
                f"{int(missing_items.sum())} returns reference missing order_items"
            )

    report.rows_rejected = 0 if report.ok else report.rows_read
    report.rows_valid = report.rows_read if report.ok else 0
    return report


def validate_raw_directory(raw_dir: Path | None = None) -> dict[str, Any]:
    settings = get_settings()
    raw_dir = raw_dir or settings.raw_path
    logger.info("Pipeline started — raw data validation")
    logger.info("Files discovered in %s", raw_dir)

    datasets: dict[str, pd.DataFrame] = {}
    reports: list[ValidationReport] = []

    for name in REQUIRED_FILES:
        path = raw_dir / f"{name}.csv"
        if not path.exists():
            report = ValidationReport(table=name, errors=[f"File not found: {path}"])
            reports.append(report)
            logger.error("Missing file: %s", path)
            continue
        df = _read_csv(path)
        datasets[name] = df
        logger.info("Rows read from %s: %s", name, f"{len(df):,}")

    # Validate in dependency order once all readable files are loaded
    for name in REQUIRED_FILES:
        if name not in datasets:
            continue
        report = validate_table(name, datasets[name], datasets)
        reports.append(report)
        if report.ok:
            logger.info("Rows validated for %s: %s", name, f"{report.rows_valid:,}")
        else:
            for err in report.errors:
                logger.error("[%s] %s", name, err)

    summary = {
        "ok": all(r.ok for r in reports),
        "tables": {
            r.table: {
                "rows_read": r.rows_read,
                "rows_valid": r.rows_valid,
                "rows_rejected": r.rows_rejected,
                "errors": r.errors,
                "warnings": r.warnings,
            }
            for r in reports
        },
    }

    out_path = settings.processed_path / "validation_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Validation report written to %s", out_path)

    if summary["ok"]:
        logger.info("Pipeline completed — validation successful")
    else:
        logger.error("Pipeline completed — validation FAILED")
    return summary


def main() -> None:
    summary = validate_raw_directory()
    if not summary["ok"]:
        raise SystemExit(1)
    print("Validation passed for all raw tables.")


if __name__ == "__main__":
    main()
