"""
Provenance Guard — Flask API.

Endpoints:
  POST /submit     run the 3-signal ensemble, return verdict + confidence + transparency label,
                   write a structured audit entry. Rate limited.
  POST /appeal     contest a classification: status -> under_review, logged beside the original.
  GET  /log        recent structured audit entries (JSON).
  GET  /analytics  platform metrics (stretch): verdict mix, appeal rate, avg confidence.
  GET  /health     liveness.
"""

import uuid

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

import audit
import store
import pipeline
import analytics

load_dotenv()

app = Flask(__name__)

# Rate limiting — see README for the reasoning behind these specific numbers.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

SUBMIT_LIMITS = "10 per minute;100 per day"

# Bring back prior content records so appeals work across restarts.
store.rehydrate_from_log()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
@limiter.limit(SUBMIT_LIMITS)
def submit():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    creator_id = (body.get("creator_id") or "").strip()

    if not text:
        return jsonify({"error": "field 'text' is required and must be non-empty"}), 400
    if not creator_id:
        return jsonify({"error": "field 'creator_id' is required"}), 400

    content_id = str(uuid.uuid4())
    result = pipeline.analyze(text)
    fusion = result["fusion"]
    label = result["label"]
    s = result["signal_scores"]

    record = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": fusion["attribution"],
        "confidence": fusion["confidence"],
        "combined_p_ai": fusion["combined_p_ai"],
        "semantic_score": s["semantic"],
        "structural_score": s["structural"],
        "lexical_score": s["lexical"],
        "label_headline": label["headline"],
        "status": "classified",
    }
    store.save(record)

    audit.append_entry({
        "type": "classification",
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": audit.now_iso(),
        "attribution": fusion["attribution"],
        "confidence": fusion["confidence"],
        "combined_p_ai": fusion["combined_p_ai"],
        "signal_scores": s,
        "signal_agreement": fusion["agreement"],
        "semantic_source": result["signals"]["semantic"]["source"],
        "label_headline": label["headline"],
        "status": "classified",
    })

    return jsonify({
        "content_id": content_id,
        "attribution": fusion["attribution"],
        "confidence": fusion["confidence"],
        "combined_p_ai": fusion["combined_p_ai"],
        "label": label,
        "signals": result["signals"],          # individual signal scores (multi-signal evidence)
        "ensemble": {
            "weights": __import__("scoring").WEIGHTS,
            "agreement": fusion["agreement"],
            "signal_spread": fusion["signal_spread"],
            "note": "Verdict = weighted mean; confidence falls as signals disagree (spread up).",
        },
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    body = request.get_json(silent=True) or {}
    content_id = (body.get("content_id") or "").strip()
    reasoning = (body.get("creator_reasoning") or "").strip()

    if not content_id:
        return jsonify({"error": "field 'content_id' is required"}), 400
    if not reasoning:
        return jsonify({"error": "field 'creator_reasoning' is required"}), 400

    rec = store.get(content_id)
    if rec is None:
        return jsonify({"error": f"no content found with content_id '{content_id}'"}), 404

    store.update_status(content_id, "under_review")

    audit.append_entry({
        "type": "appeal",
        "content_id": content_id,
        "creator_id": rec.get("creator_id"),
        "timestamp": audit.now_iso(),
        "creator_reasoning": reasoning,
        # original decision carried alongside the appeal:
        "original_attribution": rec.get("attribution"),
        "original_confidence": rec.get("confidence"),
        "original_combined_p_ai": rec.get("combined_p_ai"),
        "original_signal_scores": {
            "semantic": rec.get("semantic_score"),
            "structural": rec.get("structural_score"),
            "lexical": rec.get("lexical_score"),
        },
        "status": "under_review",
    })

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received. This content is now under human review.",
    })


@app.route("/log", methods=["GET"])
def log():
    try:
        limit = int(request.args.get("limit", 0)) or None
    except ValueError:
        limit = None
    return jsonify({"entries": audit.get_log(limit)})


@app.route("/analytics", methods=["GET"])
def analytics_view():
    return jsonify(analytics.compute())


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "rate limit exceeded",
        "limit": str(e.description),
        "message": "Too many submissions. Please slow down and try again shortly.",
    }), 429


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
