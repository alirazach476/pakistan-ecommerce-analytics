"""Stop the embedded PostgreSQL server started for local development."""

from __future__ import annotations

import embedded_postgres

from src.utils.config import PROJECT_ROOT


def main() -> None:
    data_dir = PROJECT_ROOT / ".pgdata"
    if not data_dir.exists():
        print("No .pgdata directory found.")
        return
    embedded_postgres.pg_ctl(["-w", "stop"], pgdata=str(data_dir))
    print("Embedded PostgreSQL stopped.")


if __name__ == "__main__":
    main()
