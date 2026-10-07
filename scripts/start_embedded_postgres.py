"""
Start an embedded PostgreSQL instance for local development when Docker
is unavailable. Prefer `docker compose up -d postgres` when Docker works.

Usage:
  python scripts/start_embedded_postgres.py
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import embedded_postgres
from sqlalchemy import create_engine, text

from src.utils.config import PROJECT_ROOT, get_settings


def main() -> None:
    settings = get_settings()
    data_dir = PROJECT_ROOT / ".pgdata"
    data_dir.mkdir(parents=True, exist_ok=True)

    # cleanup_mode=None keeps the server running after this process exits
    pg = embedded_postgres.get_server(str(data_dir), cleanup_mode=None)
    uri = pg.get_uri()
    print(f"Embedded PostgreSQL URI: {uri}")

    engine = create_engine(uri, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :u"),
            {"u": settings.postgres_user},
        ).scalar()
        if not exists:
            # Local portfolio only — password from .env
            conn.execute(
                text(
                    f"CREATE ROLE {settings.postgres_user} LOGIN "
                    f"PASSWORD '{settings.postgres_password}' SUPERUSER"
                )
            )
            print(f"Created role {settings.postgres_user}")

        db_exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :d"),
            {"d": settings.postgres_db},
        ).scalar()
        if not db_exists:
            conn.execute(
                text(
                    f'CREATE DATABASE "{settings.postgres_db}" OWNER {settings.postgres_user}'
                )
            )
            print(f"Created database {settings.postgres_db}")

    parsed = urlparse(uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5432

    env_local = PROJECT_ROOT / ".env"
    content = env_local.read_text(encoding="utf-8") if env_local.exists() else ""
    updates = {
        "POSTGRES_HOST": host,
        "POSTGRES_PORT": str(port),
        "POSTGRES_DB": settings.postgres_db,
        "POSTGRES_USER": settings.postgres_user,
        "POSTGRES_PASSWORD": settings.postgres_password,
    }
    lines = content.splitlines() if content else []
    keys_seen: set[str] = set()
    new_lines = []
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                keys_seen.add(key)
                continue
        new_lines.append(line)
    for key, value in updates.items():
        if key not in keys_seen:
            new_lines.append(f"{key}={value}")
    env_local.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    (data_dir / "embedded_uri.txt").write_text(uri + "\n", encoding="utf-8")
    print(f"Updated {env_local} with POSTGRES_HOST={host} POSTGRES_PORT={port}")
    print("Embedded PostgreSQL is running in the background (cleanup_mode=None).")
    print("Stop later with: python scripts/stop_embedded_postgres.py")


if __name__ == "__main__":
    main()
