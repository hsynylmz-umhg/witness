# Demo voiceover

Narration for the operator to record, split into the eight beats of `docs/DEMO_SCRIPT.md`. The
text is the script's spoken column, copied word for word; if the script changes, this file is
regenerated from it, never edited on its own. Durations are estimates at 150 words per minute
(2.5 words per second), not measured readings. No audio is synthesised.

| Beat | Slot (s) | Words | Estimated (s) | Over slot | Narration |
|---|---:|---:|---:|---|---|
| 1 | 15 | 35 | 14.0 | no | A procedure says: mark ten boxes, in order. Did it happen, and can you prove what you saw? witness answers with findings, and a finding either carries an evidence id or it does not exist. |
| 2 | 25 | 42 | 16.8 | no | The input is an event log: which part, in what order, with which still. The audit is deterministic. Coverage, ordering and undocumented parts. Here, one box has no witnessed event, so the report asks for human review instead of calling it done. |
| 3 | 20 | 43 | 17.2 | no | Every report is hash-linked: the record hash, then the HTML bytes, then the manifest. Anyone can recompute it from the output. These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together. |
| 4 | 25 | 30 | 12.0 | no | The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives. That tests the rules, not the real world. |
| 5 | 40 | 77 | 30.8 | no | Then we tried producing the event log from real footage, with deterministic geometry and no model. This is the operator's own scene: one sheet, one angle, one lighting condition. On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline. On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks. |
| 6 | 25 | 54 | 21.6 | no | So we made the masks follow the sheet, and required a clear correlation peak. On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing. We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result. |
| 7 | 20 | 46 | 18.4 | no | Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them: 78 anchor calls, 0.195 dollars, and both clips now agree with the key. The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation. |
| 8 | 10 | 14 | 5.6 | no | witness: an event log in, evidence-linked findings out, and every miss on the record. |

Total: 341 words, about 136.4 s of narration in a 180 s cut. No beat exceeds its
slot, so no words were shortened. The rest of each slot is silence over the picture.

Beat 7 changed in round 15: it now states the measured model run. The recorded `beat-07.mp3`
still speaks the old line ("Model integration is NOT_RUN…"), which is now false, so the beat-7
clip must be regenerated from the text above before the film is submitted.
