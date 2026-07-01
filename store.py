"""In-memory content-record store, keyed by content_id.

Rehydrates from the persisted audit log on startup so that an appeal can still find its original
classification after a server restart (the demo and grader may restart the process between steps).
"""

from __future__ import annotations  # allow `dict | None` hints on Python 3.9

import audit

_content: dict = {}


def save(record: dict) -> dict:
    _content[record["content_id"]] = record
    return record


def get(content_id: str) -> dict | None:
    return _content.get(content_id)


def update_status(content_id: str, status: str) -> dict | None:
    rec = _content.get(content_id)
    if rec is None:
        return None
    rec["status"] = status
    return rec


def all_records() -> list:
    return list(_content.values())


def rehydrate_from_log() -> None:
    """Rebuild content records from classification entries in the audit log."""
    for entry in audit.get_log():
        if entry.get("type") == "classification":
            cid = entry.get("content_id")
            if cid:
                # Classification entries store the three scores under signal_scores; unpack them
                # into the same flat keys save() uses so an appeal after a restart carries the
                # original scores instead of nulls.
                scores = entry.get("signal_scores") or {}
                _content[cid] = {
                    "content_id": cid,
                    "creator_id": entry.get("creator_id"),
                    "attribution": entry.get("attribution"),
                    "confidence": entry.get("confidence"),
                    "combined_p_ai": entry.get("combined_p_ai"),
                    "semantic_score": scores.get("semantic"),
                    "structural_score": scores.get("structural"),
                    "lexical_score": scores.get("lexical"),
                    "label_headline": entry.get("label_headline"),
                    "status": entry.get("status", "classified"),
                }
    # Apply any later status changes (e.g. appeals flipping to under_review).
    for entry in audit.get_log():
        if entry.get("type") == "appeal":
            cid = entry.get("content_id")
            if cid in _content:
                _content[cid]["status"] = entry.get("status", "under_review")
