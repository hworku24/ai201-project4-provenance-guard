"""Structured, append-only audit log persisted as a JSON array (audit_log.json)."""

from __future__ import annotations  # allow `int | None` hints on Python 3.9

import os
import json
import threading
from datetime import datetime, timezone

LOG_PATH = os.environ.get(
    "AUDIT_LOG_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_log.json")
)
_lock = threading.Lock()


def now_iso() -> str:
    """UTC timestamp like 2026-06-29T14:32:10.123Z."""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _load() -> list:
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def append_entry(entry: dict) -> dict:
    """Append one structured entry and persist."""
    with _lock:
        entries = _load()
        entries.append(entry)
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    return entry


def get_log(limit: int | None = None) -> list:
    entries = _load()
    if limit:
        return entries[-limit:]
    return entries
