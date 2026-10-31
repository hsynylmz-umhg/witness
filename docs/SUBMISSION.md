# Submission text

An event log in, evidence-linked findings out, every miss on the record.

WITNESS audits a fixed-camera assembly procedure from its event log. It reports skipped steps,
out-of-order steps and undocumented parts, and each finding either carries an evidence id or
does not exist. The audit is deterministic and writes a report whose hash chain anyone can
recompute from the output bytes.

We first tried producing the event log from real footage of a ten-box panel with geometry alone.
That extractor missed and invented marks, then refused both clips rather than guess, and we froze
it. A Meta segmentation model, sam-3.1, then proposed the boxes every five seconds, deterministic
code named them, and the same texture rule judged them: on both clips the audit now agrees with
the key, for 78 calls and USD 0.1950. The naming rule was calibrated on six frames from those same
clips, so this is a demonstration, not independent validation.

The limit: all 25 risk-gate cases are synthetic, and the only real footage is two clips of one
scene.

The film runs 152.2 s. Then read `docs/RISK_GATE.md` and `docs/REAL_MEDIA.md`, where every
real-footage number sits beside the key it was measured against.
