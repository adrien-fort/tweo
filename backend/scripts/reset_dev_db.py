"""Development database reset script.

Drops all tables and re-runs all Alembic migrations from scratch.
Use this to rebuild a clean dev database or to reproduce a fresh
environment for manual testing.

Usage::

    cd backend
    python scripts/reset_dev_db.py

To target a specific database, set DATABASE_URL before running::

    DATABASE_URL=sqlite:///./test.db python scripts/reset_dev_db.py

WARNING: This is destructive — all data in the database will be lost.
Never run against a production database.
"""

import os
import sys

# Refuse to run if pointed at a non-SQLite URL (production guard)
_url = os.environ.get("DATABASE_URL", "sqlite:///./tweo.db")
if not _url.startswith("sqlite"):
    print(f"ERROR: reset_dev_db.py refuses to run against a non-SQLite database: {_url}")
    print("This script is for development only.")
    sys.exit(1)

from alembic.config import Config  # noqa: E402

import app.infrastructure.persistence.models  # noqa: E402, F401 — registers all models
from alembic import command  # noqa: E402
from app.infrastructure.persistence.database import get_engine  # noqa: E402
from app.infrastructure.persistence.models.base import Base  # noqa: E402

engine = get_engine()

print(f"Resetting database: {_url}")
Base.metadata.drop_all(engine)
print("  Dropped all tables.")

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
print("  Ran all migrations.")
print("Done — database reset complete.")
