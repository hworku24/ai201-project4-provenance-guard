# Show What You Know: Provenance Guard — Project Brief

⏰ ~9–11 hours total

## Overview
Build **Provenance Guard**: a backend system that any creative sharing platform could
plug into to classify submitted content, score confidence in that classification,
surface a transparency label to users, and handle appeals from creators who believe
they've been misclassified.

Most independent project so far. No planning template — design the system architecture
from scratch before writing any implementation code.

## Grading
- 29 points total (25 required + 4 stretch). *(Grading scale to be provided by user.)*

## Deliverables & Format (easy to miss)
- **Transparency label** → written as text in README. Must include verbatim text of all
  three label variants (high-confidence AI, high-confidence human, uncertain) as a quoted
  string or markdown table. Screenshot optional; text is required.
- **Architecture diagram** → in `planning.md` under an `## Architecture` section. ASCII art
  fine (also Mermaid or embedded sketch).
- No starter repo, no planning template. Create own GitHub repo, design `planning.md`
  structure yourself. All evidence (audit-log sample, rate-limit config + chosen limits,
  label variants, appeal handling) lives in README and committed source — the canonical record.

## Goals
- Design/implement a multi-signal AI content classification pipeline.
- Build confidence scoring that communicates uncertainty rather than forcing binary outputs.
- Create end-user transparency labels that surface AI verdicts clearly and fairly.
- Implement an appeals workflow for contested classifications.
- Add production safety infrastructure: rate limiting and structured audit logging.

## Required Features
1. **Content Submission Endpoint** — API endpoint accepting text-based content for attribution
   analysis. Returns structured response: attribution result, confidence score, transparency
   label text.
2. **Multi-Signal Detection Pipeline** — at least 2 distinct signals. Single-signal not
   acceptable. planning.md and README must explain what each signal captures and why chosen.
3. **Confidence Scoring with Uncertainty** — return a confidence score, not just binary.
   0.51 must produce a meaningfully different label than 0.95. README explains approach and
   how scores were tested for meaningfulness.
4. **Transparency Label** — displayed to reader. Plain language, confidence meaningful to
   non-technical reader. README: typed description of all three variants with exact text.
5. **Appeals Workflow** — creators can contest a classification. At minimum: capture creator's
   reasoning, log appeal alongside original decision, update status to "under review".
   Automated re-classification not required.
6. **Rate Limiting** — on submission endpoint. README documents limits chosen and reasoning.
7. **Audit Log** — every decision (confidence score, signals used, appeals) captured in a
   structured audit log. Document in README (or GET /log) with ≥3 entries visible.

## Stretch Features (4 pts extra; update planning.md before starting each)
- **Ensemble detection**: 3+ signals with documented weighting/voting.
- **Provenance certificate**: "verified human" credential earned via extra verification step,
  including how it's displayed.
- **Analytics dashboard**: view of detection patterns, appeal rates, + one more metric.
- **Multi-modal support**: second content type (e.g. image descriptions / structured metadata).

## Hints
- False positive (human's work labeled AI) is worse than false negative on a writing platform.
  Confidence scoring / label design should reflect this asymmetry.
- Confidence score is a design decision before a technical one. Decide what 0.5 means to a user first.
- Transparency label is a UX problem — show it to someone unfamiliar and ask what they understand.
- Rate limiting numbers aren't arbitrary — reason about realistic writer usage vs. adversarial flooding.
- Detection needn't be perfect. Acknowledge uncertainty honestly + give appeal path.

## Recommended Stack
| Component | Tool | Notes |
|---|---|---|
| API framework | Flask | Free, lightweight |
| Detection signal 1 | Groq (llama-3.3-70b-versatile) | Free tier |
| Detection signal 2 | Stylometric heuristics | Pure Python |
| Rate limiting | Flask-Limiter | Free |
| Audit log | SQLite (built-in) or structured JSON | No setup |

### requirements.txt
```
flask>=3.0.0
flask-limiter>=3.5.0
groq==0.15.0
python-dotenv==1.0.1
```

### .env (gitignored, never commit)
```
GROQ_API_KEY=your_key_here
```

## Note on detection signals
Need ≥2 distinct signals. "Distinct" = genuinely different properties. Strong default pairing:
- **LLM-based classification (Groq)**: ask model to assess human vs AI. Captures semantic/
  stylistic coherence holistically.
- **Stylometric heuristics**: measurable statistical properties (sentence length variance,
  type-token ratio, punctuation density, avg sentence complexity). AI text more uniform;
  human more variable. Pure Python.
One semantic, one structural = more informative together.

---

## Milestone 1: Understand the System and Define Your Architecture (~30 min)
- Write in plain English the path a piece of text takes from submission to label. Name every
  component. = architecture narrative.
- Decide 2 detection signals before coding. For each: what property it measures, why it differs
  between human/AI, what it can't capture (blind spot).
- Think through false-positive problem: trace a misclassified human's work through the system.
- Sketch API surface: endpoints, what each accepts/returns.
- Turn narrative into a diagram. Two flows:
  1. Submission: POST /submit → signal 1 → signal 2 → confidence scoring → transparency label
     → audit log → response
  2. Appeal: POST /appeal → status update → audit log → response
  Label each arrow with what passes (raw text, signal score, combined score, label text).

**Checkpoint:** Can describe the full path naming every component. Chose 2 signals, can explain
what each captures/misses. Rough endpoint list. Diagram of both flows.

## Milestone 2: Write Your Spec Before Any Code (~1–2 hrs)
Create `planning.md`. Design structure yourself. Address 5 questions with specific,
implementation-ready answers:
1. **Detection signals**: what are your 2+ signals, what each measures, output shape (0–1 score?
   binary?), how to combine into single confidence score.
2. **Uncertainty representation**: what does 0.6 mean? How to map raw outputs to calibrated
   score? Thresholds separating "likely AI" / "uncertain" / "likely human".
3. **Transparency label design**: exact text for high-conf AI, high-conf human, uncertain.
4. **Appeals workflow**: who appeals, what info they provide, what the system does (status
   changes, logging), what a reviewer sees in the appeal queue.
5. **Anticipated edge cases**: ≥2 specific scenarios (e.g. "a poem with heavy repetition and
   simple vocab that heuristics might score as AI").

- `## Architecture` section: diagram from M1 + 2–3 sentence narrative.
- `## AI Tool Plan` section: for M3, M4, M5 specify which spec sections you'll provide, what
  you'll ask AI to generate, how you'll verify.
- Review/revise label variants before building. Update planning.md before any stretch features.

**Checkpoint:** planning.md answers all 5 questions. Three label variants written. Scoring
produces different labels at different ranges (not a binary flip at 0.5). Architecture section
has the diagram. AI Tool Plan covers all three implementation milestones.

## Milestone 3: Submission Endpoint + First Detection Signal (~2–3 hrs)
- Prompt AI with detection-signals section + diagram → Flask app skeleton with POST /submit
  stub + first signal function. Review carefully.
- POST /submit accepts JSON with at minimum `text` and `creator_id`. Start with hardcoded
  response to verify route.
- Implement first signal (Groq): structured assessment. Test independently first.
- Wire signal into endpoint. Response has: `content_id` (unique), attribution from signal 1,
  placeholder confidence, placeholder label. content_id essential for appeals + audit log.
- Test with curl.
- Audit log: every submit writes structured entry (timestamp, content ID, attribution, signal 1
  score). Structured JSON or SQLite, not print(). Example entry:
```json
{
  "content_id": "3f7a2b1e-...",
  "creator_id": "test-user-1",
  "timestamp": "2025-04-01T14:32:10.123Z",
  "attribution": "likely_ai",
  "confidence": 0.78,
  "llm_score": 0.81,
  "status": "classified"
}
```
- GET /log endpoint returns most recent entries as JSON.

**Checkpoint:** Flask app runs. POST /submit returns content_id, attribution, placeholder
confidence. Each submission writes structured audit entry. GET /log returns entries.

## Milestone 4: Second Signal + Confidence Scoring (~2 hrs)
- Prompt AI with detection-signals + uncertainty + diagram → second signal function + confidence
  scoring logic. Verify scoring matches your thresholds.
- Second signal (stylometric): 2–3 metrics (sentence length variance, type-token ratio),
  combine into single signal score. Test standalone on same inputs as signal 1.
- Confidence scoring: combine both per spec. Must vary meaningfully across inputs, map to ≥3
  label categories.
- Test ≥4 deliberate inputs: clearly AI, clearly human, 2 borderline. (Sample inputs provided
  in original brief.)
- Update audit log to capture both individual signal scores + combined confidence.

**Checkpoint:** Both signals running, combined into single confidence. Clearly-AI vs
clearly-human produce noticeably different scores. Audit log records individual + combined.
Tested ≥4 inputs spanning range.

## Milestone 5: Production Layer (~2–3 hrs)
- Prompt AI with label variants + appeals workflow + diagram → label generation function +
  POST /appeal endpoint. Verify label function against thresholds.
- **Transparency label**: 3 variants, label changes with confidence. Test all 3 reachable.
- **Appeals workflow**: POST /appeal accepts `content_id` + `creator_reasoning`. Updates status
  to "under review", logs appeal alongside original decision, returns confirmation. No auto
  re-classification.
- **Rate limiting**: Flask-Limiter on /submit. Choose defensible limits, document reasoning.
  Requires `storage_uri="memory://"`. Example: `@limiter.limit("10 per minute;100 per day")`.
  Test: 12 rapid requests → first 10 return 200, rest 429. Capture 429s in README.
- **Complete audit log**: timestamp, content ID, attribution, confidence, both signal scores,
  appeal-filed flag. Structured. ≥3 entries.

**Checkpoint:** All four production features working end-to-end. Label varies by confidence.
Appeals submitted + reflected in log. Rate limiting triggers. ≥3 structured entries incl. an appeal.

## Milestone 6: Document and Walk Through (~1–2 hrs)
- Write README covering all required sections (explain reasoning, not just implementation).
- Confidence-scoring section: two example submissions with noticeably different scores (one high,
  one lower) showing actual scores.
- Typed description of all three label variants (exact text).
- Known limitations: ≥1 specific content type system would misclassify + why (tied to a signal
  property).
- Spec reflection: one way spec helped, one way implementation diverged and why.
- AI usage section: ≥2 specific instances (what you directed, what it produced, what you revised).
- Record short portfolio walkthrough video (a couple minutes).

**Checkpoint:** README covers all sections with substantive design-decision explanations. All
three label variants written. Walkthrough recorded.

## Submission Checklist (Course Portal)
- Link to GitHub repository
- `planning.md` in repo root (written before implementation, updated before stretch features)
- `README.md` including:
  - Architecture overview (path from input to transparency label)
  - Detection signals (what each measures, why chosen, what it misses)
  - Confidence scoring (how combined, how validated, two example submissions with actual scores)
  - Transparency label (typed description of all three variants with exact text; screenshot optional)
  - Rate limiting (limits + reasoning)
  - Known limitations (≥1 specific misclassified content type + why)
  - Spec reflection (one help, one divergence)
  - AI usage section (≥2 specific instances)
- Short portfolio walkthrough video (a couple minutes)
