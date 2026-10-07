"""Extract raw CSV / JSON files from the landing zone."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.config import get_settings
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

TABLE_ORDER = [
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


def discover_files(raw_dir: Path | None = None) -> dict[str, Path]:
    settings = get_settings()
    raw_dir = raw_dir or settings.raw_path
    discovered: dict[str, Path] = {}
    for table in TABLE_ORDER:
        path = raw_dir / f"{table}.csv"
        if path.exists():
            discovered[table] = path
            logger.info("Discovered file: %s", path.name)
        else:
            logger.warning("Expected file missing: %s", path)
    return discovered


def extract_table(path: Path) -> pd.DataFrame:
    logger.info("Reading %s", path.name)
    df = pd.read_csv(path, low_memory=False)
    logger.info("Rows read: %s from %s", f"{len(df):,}", path.name)
    return df


def extract_all(raw_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    files = discover_files(raw_dir)
    data: dict[str, pd.DataFrame] = {}
    for table, path in files.items():
        data[table] = extract_table(path)
    return data
