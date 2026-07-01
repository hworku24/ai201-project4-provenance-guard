# Project 4: Provenance Guard — Grading Rubric
**Total: 25 pts + 4 pts bonus**

## Required Features (25 pts)

### Content Submission Endpoint — 3 pts
- [ ] 1 — Demo/source shows a text submission returning a structured JSON response.
- [ ] 1 — Response includes an attribution result AND a confidence score.
- [ ] 1 — Response includes transparency label text (not just a raw score).

### Multi-Signal Detection Pipeline — 2 pts
- [ ] 1 — README names 2+ signals; explains what property of text each measures AND what each misses.
- [ ] 1 — Demo/source shows results reflecting both signals (e.g. individual signal scores shown with combined).

### Confidence Scoring with Uncertainty — 2 pts
- [ ] 1 — Demo/source shows ≥2 submissions with noticeably different confidence (high + lower case).
- [ ] 1 — README explains how signals are combined AND how student validated scores are meaningful
        (tested inputs / described thresholds).

### Transparency Label — 3 pts
- [ ] 1 — README includes label's actual text as quoted string or markdown table (screenshot optional).
- [ ] 1 — Label uses plain language — no jargon ("classifier output", "logit score"). Non-technical reader understands.
- [ ] 1 — Label visibly differs between high-conf and low-conf results — different text, not just a number.

### Appeals Workflow — 2 pts
- [ ] 1 — Demo/source shows an appeal submitted with creator reasoning included.
- [ ] 1 — Demo/source shows status updated to "under review" AND appeal visible in audit log.

### Rate Limiting — 2 pts
- [ ] 1 — Demo/source shows rate limiting in action (429 response / error when limit hit).
- [ ] 1 — README documents specific limits + reasoning tied to realistic writing-platform usage (not "default").

### Audit Log — 3 pts
- [ ] 1 — Demo/source shows ≥3 entries; each visibly includes attribution result, confidence score, timestamp.
- [ ] 1 — Log format is structured (JSON, table, formatted log file). Unformatted console output does NOT qualify.
- [ ] 1 — ≥1 appeal visible in log, showing appeal alongside original classification entry.

### planning.md — 4 pts
- [ ] 1 — Detection signals described: what each measures + how outputs combined.
- [ ] 1 — Uncertainty representation: specific thresholds / score ranges defined (not just "shows a score").
- [ ] 1 — Transparency label variants written out for high-conf AI, uncertain, AND high-conf human.
- [ ] 1 — Appeals workflow + ≥2 anticipated edge cases described specifically; `## AI Tool Plan` section
        identifies ≥1 milestone using AI codegen, specifying what spec sections + diagram provided as input.

### README — 2 pts
- [ ] 1 — Known limitations names ≥1 specific content type likely misclassified, tied to the signals
        (not a generic disclaimer).
- [ ] 1 — Spec reflection present + substantive — real way implementation diverged from plan + why.

### AI Usage — 2 pts
- [ ] 1 — Describes ≥2 specific instances: what student directed AI to do + what the output was.
- [ ] 1 — Each instance includes what student revised/overrode/decided differently (not just "I used AI").

## Stretch Features (+4 pts)
- [ ] +1 — **Ensemble Detection**: README describes 3+ distinct signals with documented weighting/voting
        strategy resolving conflicts. Demo/source shows individual scores alongside ensemble result.
- [ ] +1 — **Provenance Certificate**: README describes certificate design + verification step to earn it.
        Demo/source shows a verified label distinguishable from standard transparency label.
- [ ] +1 — **Analytics Dashboard**: Demo/source shows view with ≥3 metrics: detection pattern
        (AI vs human ratio), appeal rate, + one more.
- [ ] +1 — **Multi-Modal Support**: Demo/source shows a non-text content type processed through pipeline
        returning a result. README describes how pipeline handles it + what signals used.

## Point-maximizing notes
- Every "Demo or source shows..." item can be satisfied by committed source + README evidence
  (curl output, log dumps). We'll paste real output into README.
- Structured audit log (JSON/SQLite) is worth being strict about — no print() statements.
- Label text must differ by *wording* across confidence bands, not just number.
- AI Usage + Spec Reflection are free points if we keep notes as we build — track them live.
