"""
Analytics (stretch feature) — computes platform-level metrics from the audit log.

Metrics:
  - detection pattern: counts/ratios of likely_ai / uncertain / likely_human verdicts
  - appeal rate: appeals / classifications
  - average confidence (the additional metric of choice), plus a low-confidence share
"""

import audit


def compute() -> dict:
    entries = audit.get_log()
    classifications = [e for e in entries if e.get("type") == "classification"]
    appeals = [e for e in entries if e.get("type") == "appeal"]

    n = len(classifications)
    counts = {"likely_ai": 0, "uncertain": 0, "likely_human": 0}
    confidences = []
    for e in classifications:
        attr = e.get("attribution")
        if attr in counts:
            counts[attr] += 1
        c = e.get("confidence")
        if isinstance(c, (int, float)):
            confidences.append(c)

    ratios = {k: round(v / n, 3) if n else 0.0 for k, v in counts.items()}
    avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else None
    low_conf_share = (
        round(sum(1 for c in confidences if c < 0.70) / len(confidences), 3)
        if confidences else None
    )

    return {
        "total_classifications": n,
        "verdict_counts": counts,
        "verdict_ratios": ratios,                       # detection pattern
        "total_appeals": len(appeals),
        "appeal_rate": round(len(appeals) / n, 3) if n else 0.0,   # appeal rate
        "average_confidence": avg_conf,                 # additional metric
        "low_confidence_share": low_conf_share,         # share shown 'uncertain' on confidence
    }
