"""
Detection pipeline orchestration.

Runs all three signals, fuses them with the weighted ensemble, and selects the transparency label.
Returns one structured result used by both /submit and the audit log.
"""

import signals
import stylometry
import scoring


def analyze(text: str) -> dict:
    sem = signals.llm_semantic_signal(text)        # Signal 1 — semantic
    sty = stylometry.stylometry_signal(text)       # Signal 2 — structural
    lex = signals.lexical_signal(text)             # Signal 3 — lexical (ensemble)

    signal_scores = {
        "semantic": sem["llm_score"],
        "structural": sty["stylometry_score"],
        "lexical": lex["lexical_score"],
    }
    fused = scoring.score(signal_scores)

    # Label engine imports CONFIDENCE_GATE from scoring; import here to avoid a cycle at module load.
    import labels
    label = labels.label_for(fused["attribution"], fused["confidence"])

    return {
        "signals": {
            "semantic": {"score": sem["llm_score"], "source": sem["source"],
                         "rationale": sem["rationale"]},
            "structural": {"score": sty["stylometry_score"], "metrics": sty["metrics"],
                           "short_text": sty["short_text"]},
            "lexical": {"score": lex["lexical_score"], "detail": lex["detail"]},
        },
        "signal_scores": signal_scores,
        "fusion": fused,
        "label": label,
    }
