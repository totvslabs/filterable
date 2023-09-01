"""Helper to make PostgreSQL JSONB type work in SQLite with SQLAlchemy."""

import sys
from sqlalchemy.types import JSON


def JSONB(sqlite_json=JSON):
    """Return a JSONB type, or a JSON type on SQLite."""
    try:
        from sqlalchemy.dialects.postgresql import JSONB
        # Workaround for lack of support for JSONB in SQLite
        return JSON if "pytest" in sys.modules else JSONB
    except ImportError:
        return sqlite_json