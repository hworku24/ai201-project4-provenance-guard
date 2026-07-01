# Provenance Guard — Status & Authoritative Design

> IMPORTANT: A COMPLETE implementation already existed in the repo (dated Jun 29) before this
> session. We chose to **verify & complete** it, not rebuild. The existing files + the existing
> `planning.md`/`README.md` are AUTHORITATIVE. Ignore any earlier "fresh design" notes.

## What the existing system actually does
- **Stack:** Flask + Flask-Limiter (memory://), Groq (with offline fallback), python-dotenv.
- **Signals (3 — ensemble stretch built in):**
  1. Semantic (Groq `llama-3.3-70b-versatile`; offline register heuristic when no key).
  2. Structural stylometry (sentence-length CV burstiness, mean sentence length, punctuation).
  3. Lexical fingerprint (AI-cliché vs casual-human markers).
- **Fusion:** `combined_p_ai = 0.55*semantic + 0.25*structural + 0.20*lexical`.
- **Two numbers:** `combined_p_ai` (which way) + `confidence` (how sure).
  - `extremity = 2*|p-0.5|`; `agreement = 1 - spread`; `confidence = 0.6*extremity + 0.4*agreement`.
- **Bands:** likely_human `<0.40` · uncertain `0.40–0.70` · likely_ai `≥0.70`.
- **Confidence gate 0.70:** a low-confidence AI/human lean collapses to the "uncertain" LABEL
  (false-positive protection).
- **Storage:** append-only JSON audit log (`audit_log.json`) + in-memory content store that
  rehydrates from the log on startup. (NOTE: we did NOT switch to SQLite — JSON is what's built
  and it satisfies "structured".)
- **Endpoints:** POST /submit, POST /appeal, GET /log, GET /analytics (stretch), GET /health.
- **Rate limit:** `10 per minute; 100 per day` on /submit.

## Work done this session
1. Fixed Python 3.9 incompatibility: added `from __future__ import annotations` to `audit.py`
   and `store.py` (they used `int | None` / `dict | None` hints; user's default python3 is 3.9.6).
2. Fixed `store.rehydrate_from_log()`: it read `llm_score`/`stylometry_score` (never present);
   now unpacks `signal_scores` → semantic/structural/lexical so appeals after a restart carry
   real scores instead of nulls.
3. Verified: `test_app.py` passes; all module self-tests run; rate-limit evidence reproduced
   exactly (10×200, 2×429); sample_audit_log.json valid.

## Rubric status: ~27/29 (25 required + 2 stretch: ensemble + analytics)

## Remaining (user actions, not code)
- Create GitHub repo + push (offer `git init` + commit when user asks — NOT done automatically).
- Record the ~2-min portfolio walkthrough video.
- OPTIONAL: add real GROQ_API_KEY to `.env` to run signal 1 as true semantic (stronger evidence);
  offline fallback is documented and acceptable without it.

## Venv
- `.venv` created with Python 3.9.6; deps installed from requirements.txt.
