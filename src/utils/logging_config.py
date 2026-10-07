"""Structured logging for pipelines and CLI tools."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.utils.config import get_settings


def setup_logging(name: str = "pk_ecommerce", level: str | None = None) -> logging.Logger:
    """Configure console + file logging and return a named logger."""
    settings = get_settings()
    log_level = (level or settings.log_level).upper()
    logs_dir = settings.logs_path
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(log_level)
    logger.addHandler(console)

    file_handler = logging.FileHandler(logs_dir / "pipeline.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
