"""
Confidence scoring / fusion layer (Milestone 4 + Ensemble stretch).

Combines the detection signals into:
  - combined_p_ai : weighted-ensemble probability-of-AI used for the attribution verdict
  - confidence    : how sure we are in that verdict (drops when the signals disagree)

The fusion is a documented WEIGHTED ENSEMBLE. Conflict resolution: the weighted mean sets the
verdict, while disagreement among signals (their spread) lowers confidence — and a verdict that
doesn't clear the confidence gate is shown to the reader as "uncertain" rather than a verdict.

Ensemble weights (sum to 1.0):
    semantic (LLM)   0.55   — most reliable; reads meaning/voice
    structural       0.25   — corroborating shape of the text
    lexical          0.20   — surface fingerprints; noisiest, lowest weight

For the 2-signal required pipeline (semantic + structural only) the same functions are used with
two weights; `agreement = 1 - spread` reduces to `1 - |a - b|`, identical to the original 2-signal
formula in planning.md §2.
"""

# Ensemble weights by signal name.
WEIGHTS = {
    "semantic": 0.55,
    "structural": 0.25,
    "lexical": 0.20,
}

# Attribution thresholds on combined_p_ai (planning.md §2) — deliberately asymmetric.
T_AI = 0.70        # >= this -> likely_ai
T_HUMAN = 0.40     # <  this -> likely_human ; the [0.40, 0.70) band is "uncertain"

# Confidence formula weights (planning.md §2).
W_EXTREMITY = 0.6
W_AGREEMENT = 0.4

# A verdict must clear this confidence to earn a confident label; below it the label collapses
# to "uncertain" (false-positive aversion — planning.md §2).
CONFIDENCE_GATE = 0.70


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def attribution_from_p_ai(p_ai: float) -> str:
    if p_ai >= T_AI:
        return "likely_ai"
    if p_ai < T_HUMAN:
        return "likely_human"
    return "uncertain"


def score(signal_scores: dict) -> dict:
    """Fuse a dict of {signal_name: score_0_1} into combined_p_ai + confidence + attribution.

    signal_scores must use keys present in WEIGHTS (e.g. 'semantic', 'structural', 'lexical').
    Pass only {'semantic', 'structural'} for the 2-signal required pipeline.
    """
    names = [n for n in signal_scores if n in WEIGHTS]
    total_w = sum(WEIGHTS[n] for n in names)
    combined_p_ai = _clamp(sum(WEIGHTS[n] * signal_scores[n] for n in names) / total_w)

    vals = [signal_scores[n] for n in names]
    spread = (max(vals) - min(vals)) if len(vals) >= 2 else 0.0
    agreement = 1.0 - spread                              # 1 when all signals agree
    extremity = 2.0 * abs(combined_p_ai - 0.5)            # 0 at the midpoint, 1 at the extremes
    confidence = _clamp(W_EXTREMITY * extremity + W_AGREEMENT * agreement)

    attribution = attribution_from_p_ai(combined_p_ai)

    return {
        "combined_p_ai": round(combined_p_ai, 3),
        "confidence": round(confidence, 3),
        "attribution": attribution,
        "confident": confidence >= CONFIDENCE_GATE,
        "extremity": round(extremity, 3),
        "agreement": round(agreement, 3),
        "signal_spread": round(spread, 3),
    }


if __name__ == "__main__":
    cases = {
        "clearly_human":  {"semantic": 0.21, "structural": 0.17, "lexical": 0.20},
        "uniform_ai":     {"semantic": 0.96, "structural": 0.78, "lexical": 0.90},
        "short_ai_split": {"semantic": 0.98, "structural": 0.52, "lexical": 0.90},
        "formal_human":   {"semantic": 0.68, "structural": 0.80, "lexical": 0.50},
    }
    for name, s in cases.items():
        print(f"{name:16s} -> {score(s)}")
