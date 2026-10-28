# Submission text

An event log in, evidence-linked findings out, every miss on the record.

WITNESS audits a fixed-camera assembly procedure from its event log. It reports skipped steps,
out-of-order steps and undocumented parts, and each finding either carries an evidence id or
does not exist. The audit is deterministic, makes no model call, and writes a report whose hash
chain anyone can recompute from the output bytes.

We also tried producing the event log from real footage of a ten-box panel, using geometry
alone. On one clip it found 9 of 10 marks in order, and on the other it caught the swapped
steps but flagged a box that was never marked. When we made the masks follow the sheet, the
extractor refused both clips rather than guess. We kept the refusal and did not lower the bar.

The limit: all 25 risk-gate cases are synthetic, and the only real footage is two clips
of one scene, on which perception disagreed with the answer key.

Look first at the risk-gate table in `docs/RISK_GATE.md`, then at `docs/REAL_MEDIA.md`, where
every real-footage number sits next to the key it was measured against.
