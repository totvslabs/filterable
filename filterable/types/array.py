import sys
from sqlalchemy import String
from sqlalchemy.types import JSON

def ARRAY(sqlite_array=JSON):
    """Return an ARRAY type, or a JSON type on SQLite."""
    try:
        from sqlalchemy.dialects.postgresql import ARRAY
        # Workaround for lack of support for ARRAY in SQLite
        return JSON if "pytest" in sys.modules else ARRAY(String)
    except ImportError:
        return sqlite_array
