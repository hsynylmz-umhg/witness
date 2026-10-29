# Demo script — three minutes

Beat-by-beat script for the submission video. The claim follows D030 and D031: witness verifies
an event log against a procedure and links every finding to evidence and a recomputable hash
chain. It does not claim to detect pencil marks reliably from pixels. Every spoken number names
its source file. Assets are listed in `docs/DEMO_ASSETS.md`.

| # | Time | Seconds | On screen | Spoken | Sources |
|---|---|---:|---|---|---|
| 1 | 0:00–0:15 | 15 | Source clip, clean run | "A procedure says: mark ten boxes, in order. Did it happen, and can you prove what you saw? witness answers with findings, and a finding either carries an evidence id or it does not exist." | `docs/AGENT_GUIDE.md` |
| 2 | 0:15–0:40 | 25 | `report.html`, clean clip: finding list, evidence still | "The input is an event log: which part, in what order, with which still. The audit is deterministic. Coverage, ordering and undocumented parts. Here, one box has no witnessed event, so the report asks for human review instead of calling it done." | `artifacts/real_clean_02/report.html`, `docs/REAL_MEDIA.md` (Round 7) |
| 3 | 0:40–1:00 | 20 | Terminal: recompute `report_hash` and `manifest.sha256` | "Every report is hash-linked: the record hash, then the HTML bytes, then the manifest. Anyone can recompute it from the output. These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together." | `docs/RULES.md`, `artifacts/real_clean_02/manifest.json` |
| 4 | 1:00–1:21.4 | 21.40 | `docs/RISK_GATE.md` table | "The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives. That tests the rules, not the real world." | `docs/RISK_GATE.md` |
| 5 | 1:21.4–2:01.4 | 40 | Overlay still, then both real reports next to the key | "Then we tried producing the event log from real footage, with deterministic geometry and no model. This is the operator's own scene: one sheet, one angle, one lighting condition. On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline. On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks." | `docs/REAL_MEDIA.md` (Round 7), `artifacts/overlays/real_clean_02_frame-7224.png` |
| 6 | 2:01.4–2:26.4 | 25 | `docs/REAL_MEDIA.md` Round 8 refusal line | "So we made the masks follow the sheet, and required a clear correlation peak. On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing. We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result." | `docs/REAL_MEDIA.md` (Round 8), `docs/DECISIONS.md` (D030, D031) |
| 7 | 2:26.4–2:50 | 23.60 | `docs/REAL_MEDIA.md` Model-produced events table | "Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them: 78 anchor calls, 0.195 dollars, and both clips now agree with the key. The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation." | `docs/REAL_MEDIA.md` (Model-produced events), `docs/MODEL_SPIKE.md` (Round 14), `docs/DECISIONS.md` (D032, D033) |
| 8 | 2:50–3:00 | 10 | Report header with hashes | "witness: an event log in, evidence-linked findings out, and every miss on the record." | `docs/DECISIONS.md` (D030) |

Total: 180 seconds.

Not said, on purpose: any detection accuracy beyond the two clips, any model claim beyond the
measured run in beat 7, any test count, and any statement about torque, tightening or assembly
correctness.
