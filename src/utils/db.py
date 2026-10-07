"""Database connection helpers for PostgreSQL."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def get_engine(echo: bool = False) -> Engine:
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=echo,
    )


@contextmanager
def get_connection() -> Generator:
    engine = get_engine()
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
        engine.dispose()


def execute_sql_file(engine: Engine, relative_path: str | Path) -> None:
    path = Path(relative_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
    logger.info("Executed SQL file: %s", path.name)


def table_row_count(engine: Engine, schema: str, table: str) -> int:
    query = text(f'SELECT COUNT(*) AS cnt FROM "{schema}"."{table}"')
    with engine.connect() as conn:
        result = conn.execute(query).scalar()
    return int(result or 0)


def bulk_insert_dataframe(
    engine: Engine,
    df: pd.DataFrame,
    schema: str,
    table: str,
    batch_size: int | None = None,
    if_exists: str = "append",
) -> int:
    """Insert a DataFrame into PostgreSQL using batched to_sql."""
    if df.empty:
        logger.warning("No rows to insert into %s.%s", schema, table)
        return 0

    settings = get_settings()
    chunksize = batch_size or settings.batch_size
    df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
        method="multi",
        chunksize=chunksize,
    )
    logger.info("Inserted %s rows into %s.%s", f"{len(df):,}", schema, table)
    return len(df)


def truncate_tables(engine: Engine, schema: str, tables: Iterable[str]) -> None:
    """Truncate tables in reverse dependency-safe order (caller provides order)."""
    with engine.begin() as conn:
        for table in tables:
            conn.execute(text(f'TRUNCATE TABLE "{schema}"."{table}" CASCADE'))
            logger.info("Truncated %s.%s", schema, table)
