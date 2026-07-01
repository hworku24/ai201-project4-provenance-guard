"""
End-to-end verification for Provenance Guard. Run: python test_app.py

Exercises every required feature in-process (no server needed) and asserts the key behaviors:
all three labels reachable, confidence varies, appeals update status + log, audit log structured,
and rate limiting triggers a 429.
"""

import os
import tempfile

# Use a throwaway audit log so the test never touches a real one.
os.environ["AUDIT_LOG_PATH"] = os.path.join(tempfile.gettempdir(), "pg_test_audit.json")
if os.path.exists(os.environ["AUDIT_LOG_PATH"]):
    os.remove(os.environ["AUDIT_LOG_PATH"])

import app  # noqa: E402

CLEAR_AI = (
    "In today's rapidly evolving digital landscape, organizations must continually leverage "
    "innovative technological solutions in order to remain competitive within their respective "
    "markets. Furthermore, it is important to note that stakeholders across various sectors must "
    "collaborate effectively in order to achieve sustainable and optimal outcomes. Moreover, the "
    "implementation of robust strategic initiatives plays a crucial role in driving long-term "
    "organizational growth and operational efficiency."
)
CLEAR_HUMAN = (
    "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was "
    "fine but they put WAY too much sodium in it and i was thirsty for like three hours after. "
    "probably won't go back unless someone drags me there"
)
FORMAL_HUMAN = (
    "The relationship between monetary policy and asset price inflation has been extensively studied "
    "in the literature. Central banks face a fundamental tension between their mandate for price "
    "stability and the unintended consequences of prolonged low interest rates."
)


def main():
    c = app.app.test_client()

    assert c.get("/health").get_json()["status"] == "ok"

    ai = c.post("/submit", json={"text": CLEAR_AI, "creator_id": "ai"}).get_json()
    hu = c.post("/submit", json={"text": CLEAR_HUMAN, "creator_id": "hu"}).get_json()
    fm = c.post("/submit", json={"text": FORMAL_HUMAN, "creator_id": "fm"}).get_json()

    # Structured response includes attribution, confidence, label text, and individual signals.
    for r in (ai, hu, fm):
        assert "content_id" in r and "attribution" in r and "confidence" in r
        assert r["label"]["headline"] and r["label"]["body"]
        assert {"semantic", "structural", "lexical"} <= set(r["signals"].keys())

    # All three label variants reachable.
    labels = {ai["label"]["headline"], hu["label"]["headline"], fm["label"]["headline"]}
    assert labels == {"Likely AI-generated", "Likely human-written", "Attribution uncertain"}, labels

    # Confidence varies meaningfully.
    assert ai["confidence"] - fm["confidence"] > 0.15

    # False-positive guard: formal human leans AI but is NOT shown the AI label.
    assert fm["combined_p_ai"] > 0.5 and fm["label"]["headline"] == "Attribution uncertain"

    # Validation.
    assert c.post("/submit", json={"creator_id": "x"}).status_code == 400

    # Appeal updates status and logs alongside the original.
    ap = c.post("/appeal", json={"content_id": fm["content_id"],
                                 "creator_reasoning": "I wrote this; formal ESL register."})
    assert ap.status_code == 200 and ap.get_json()["status"] == "under_review"
    assert c.post("/appeal", json={"content_id": "nope", "creator_reasoning": "x"}).status_code == 404

    log = c.get("/log").get_json()["entries"]
    assert len(log) >= 3
    appeal_entries = [e for e in log if e["type"] == "appeal"]
    assert appeal_entries and appeal_entries[0]["status"] == "under_review"
    assert appeal_entries[0]["creator_reasoning"]

    # Analytics.
    a = c.get("/analytics").get_json()
    assert a["total_classifications"] == 3 and a["total_appeals"] == 1

    # Rate limiting (fresh client; limiter memory is process-global so do this last).
    codes = [c.post("/submit", json={"text": "rate limit test sentence here.",
                                      "creator_id": "rl"}).status_code for _ in range(14)]
    assert 429 in codes, codes

    print("ALL CHECKS PASSED")
    print(f"  AI label='{ai['label']['headline']}' conf={ai['confidence']}")
    print(f"  HUMAN label='{hu['label']['headline']}' conf={hu['confidence']}")
    print(f"  FORMAL label='{fm['label']['headline']}' conf={fm['confidence']} (p_ai={fm['combined_p_ai']})")
    print(f"  rate-limit status codes: {codes}")


if __name__ == "__main__":
    main()
