"""
Time helpers for harness timestamps.

Python 3.13 deprecates ``datetime.utcnow()`` because it returns a naive
datetime. The harness persists timestamps as ISO strings, so use an explicit
UTC timezone for new records while keeping the same string-based contract.
"""
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return the current UTC time as a timezone-aware ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()
