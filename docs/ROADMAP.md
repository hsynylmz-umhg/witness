# Roadmap and acceptance gates

The historical plan described an ambitious 10-day build. Dates below are internal
planning targets, not delivery promises or verified organizer deadlines. Submission
dates, eligibility, judging rules and prizes require a current portal check before
any submission. The current round authorizes offline perception-contract and estimator risk work only.

| Stage | Original internal window (2026) | Deliverable | Gate / current state |
|---|---|---|---|
| M0 Foundation | 26 October | Inventory, local environment, shared rules, API/credit record | Offline foundation complete; account/live integration gates remain explicit |
| M1 Perception spike | 27 October | 20–30 second real video, SAM masks/IDs, overlay, source-time mapping | Partial: offline ingest, codec/output conformance and sampling work; real mask/ID quality not evaluated |
| M2 Motion | 28–29 October | Axis/quality series, motion candidates, hand labels | Synthetic estimator measured separately; real >=8/10 clean-event and precision gate NOT_RUN |
| M3 Audit | 30 October | Human-reviewed procedure JSON, step-instance matching, ordering/coverage | Not implemented; clean, omitted and reordered ground truth cases required |
| M4 Vertical slice | 31 October | Video -> JSON/HTML, replay, manifest verification | Not implemented; identical input/config must reproduce deterministic derived results |
| M5 Product | 1–2 November | Small UI; optional PDF/voice | Deferred until core gate passes |
| M6 Evaluation | 2–3 November | Separate test set, metrics, ablation, limitations | Not run; report denominators, latency and real costs |
| M7 Delivery | 3–4 November | Real demo, README, contribution/source records | No publication or submission authorized in this task |

If geometry is unreliable, document a fallback decision: visible manipulation plus
reviewed part ROI, or human-marked event windows with automatic evidence association.
Label the fallback and do not report it as successful automatic tightening detection.

An alternative provider or coverage planner can be reconsidered only after M4 and
with evaluation/demo time remaining. Preserve a demo/evaluation buffer. Remove
optional scope before weakening the core evidence and uncertainty requirements.
See docs/DECISIONS.md for material corrections to the historical design.
