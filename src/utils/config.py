"""Application configuration loaded from environment variables and YAML."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings for the analytics platform."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "pakistan_ecommerce"
    postgres_user: str = "analytics"
    postgres_password: str = "change_me_secure_password"

    dbt_profiles_dir: str = "./dbt"
    dbt_target: str = "dev"

    num_customers: int = 100_000
    num_products: int = 5_000
    num_sellers: int = 1_000
    num_orders: int = 300_000
    num_returns: int = 30_000
    data_start_date: str = "2023-01-01"
    data_end_date: str = "2025-12-31"
    random_seed: int = 42

    batch_size: int = 10_000
    log_level: str = "INFO"
    raw_data_dir: str = "./data/raw"
    processed_data_dir: str = "./data/processed"
    exports_dir: str = "./data/exports"
    logs_dir: str = "./logs"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def raw_path(self) -> Path:
        path = Path(self.raw_data_dir)
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def processed_path(self) -> Path:
        path = Path(self.processed_data_dir)
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def exports_path(self) -> Path:
        path = Path(self.exports_dir)
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def logs_path(self) -> Path:
        path = Path(self.logs_dir)
        return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache
def get_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return Settings()


@lru_cache
def load_yaml_config() -> dict[str, Any]:
    config_path = PROJECT_ROOT / "config" / "settings.yaml"
    with open(config_path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_path(relative: str | Path) -> Path:
    path = Path(relative)
    return path if path.is_absolute() else PROJECT_ROOT / path
