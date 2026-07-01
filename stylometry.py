"""
Signal 2 — Stylometric heuristics (pure Python, no external libraries).

Measures the statistical *shape* of the text, blind to its meaning. Three sub-metrics, each mapped
to a 0..1 "AI-likeness" (high = uniform = AI-like), then blended:

    stylometry_score = 0.45 * uniformity_burstiness   # sentence-length variance (coeff. of variation)
                     + 0.30 * uniformity_length        # average sentence length / complexity
                     + 0.25 * uniformity_punct          # expressive-punctuation density

Rationale: AI prose tends to be statistically uniform (low sentence-length variance, longer and
more even sentences, less varied punctuation); human prose is more variable. This signal is
deliberately blind to meaning, which is exactly why it is independent of the semantic LLM signal.

NOTE ON TTR (divergence from the original plan): planning.md first specced type-token ratio as the
second metric. In testing, TTR proved badly length-biased — on the short submissions typical of a
writing platform almost every text scores high diversity, so TTR read "human" for AI and human text
alike and added no separation. It was replaced with average sentence length, which discriminates
reliably on short text. TTR is still computed and reported (informational) but is NOT part of the
score. See the README spec-reflection section.
"""

import re
import math

# Sub-metric weights inside the stylometry blend.
W_BURST = 0.45
W_LENGTH = 0.30
W_PUNCT = 0.25

# Calibration constants (documented in planning.md / README).
CV_HUMAN_FLOOR = 0.60      # CV >= this reads fully "human/bursty" -> uniformity 0
LEN_HUMAN = 10.0          # mean sentence length <= this reads human -> uniformity 0
LEN_AI = 22.0             # mean sentence length >= this reads AI-like -> uniformity 1
PUNCT_HUMAN = 0.60        # expressive marks per sentence >= this reads human -> uniformity 0


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p for p in parts if p.strip()]


def _words(text):
    return re.findall(r"[a-zA-Z']+", text.lower())


def stylometry_signal(text):
    """Return the combined stylometry_score plus the sub-metrics for transparency."""
    sentences = _split_sentences(text)
    all_words = _words(text)
    n_words = len(all_words)

    lengths = [len(_words(s)) for s in sentences]

    # --- 1. Sentence-length burstiness (coefficient of variation) ---
    if len(lengths) >= 2 and sum(lengths) > 0:
        mean_len = sum(lengths) / len(lengths)
        var = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        cv = math.sqrt(var) / mean_len if mean_len > 0 else 0.0
    else:
        mean_len = float(n_words)
        cv = None  # too few sentences to judge variance meaningfully
    uniformity_burstiness = 0.5 if cv is None else 1.0 - _clamp(cv / CV_HUMAN_FLOOR)

    # --- 2. Average sentence length / complexity ---
    uniformity_length = _clamp((mean_len - LEN_HUMAN) / (LEN_AI - LEN_HUMAN))

    # --- 3. Expressive-punctuation density ---
    expressive = len(re.findall(r"[—–\-;:()\"…]|\.\.\.|[!?]", text))
    per_sentence = expressive / max(len(sentences), 1)
    uniformity_punct = 1.0 - _clamp(per_sentence / PUNCT_HUMAN)

    score = (
        W_BURST * uniformity_burstiness
        + W_LENGTH * uniformity_length
        + W_PUNCT * uniformity_punct
    )
    score = _clamp(score)

    # Informational only (not part of the score): type-token ratio.
    ttr = len(set(all_words)) / n_words if n_words else None

    return {
        "stylometry_score": round(score, 3),
        "metrics": {
            "sentence_count": len(sentences),
            "sentence_length_cv": round(cv, 3) if cv is not None else None,
            "mean_sentence_length": round(mean_len, 2),
            "expressive_punct_per_sentence": round(per_sentence, 3),
            "type_token_ratio_informational": round(ttr, 3) if ttr is not None else None,
            "uniformity_burstiness": round(uniformity_burstiness, 3),
            "uniformity_length": round(uniformity_length, 3),
            "uniformity_punct": round(uniformity_punct, 3),
        },
        "short_text": cv is None,  # structural signal is unreliable on very short text
    }


if __name__ == "__main__":
    samples = {
        "clearly_ai": (
            "Artificial intelligence represents a transformative paradigm shift in modern society. "
            "It is important to note that while the benefits of AI are numerous, it is equally "
            "essential to consider the ethical implications. Furthermore, stakeholders across "
            "various sectors must collaborate to ensure responsible deployment."
        ),
        "clearly_human": (
            "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the "
            "broth was fine but they put WAY too much sodium in it and i was thirsty for like three "
            "hours after. my friend got the spicy version and said it was better. probably won't go "
            "back unless someone drags me there"
        ),
        "formal_human": (
            "The relationship between monetary policy and asset price inflation has been extensively "
            "studied in the literature. Central banks face a fundamental tension between their "
            "mandate for price stability and the unintended consequences of prolonged low interest "
            "rates on equity and real estate valuations."
        ),
        "edited_ai": (
            "I've been thinking a lot about remote work lately. There are genuine tradeoffs - "
            "flexibility and no commute on one side, isolation and blurred work-life boundaries on "
            "the other. Studies show productivity varies widely by individual and role type."
        ),
    }
    for name, txt in samples.items():
        r = stylometry_signal(txt)
        print(f"{name:14s} -> stylometry_score={r['stylometry_score']}  metrics={r['metrics']}")
