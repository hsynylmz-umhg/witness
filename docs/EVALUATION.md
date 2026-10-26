# Evaluation and recording protocol

## First required real recording

Record 20–30 seconds of your permitted civil mock panel using a fixed phone/tripod,
good steady lighting and 4–10 clearly numbered fasteners. Keep the actual tool,
handle and socket visible. Perform a few slow visible movements, pause, briefly
occlude the tool, then show it again. If available, add panel corner markers for
future camera-stability checks. Name the tool actually used; no torque claim.

Keep faces, personal documents and sensitive/third-party hardware out of frame.
Keep the original MP4/MOV and its timestamps; do not edit, transcode or replace it
with a social-media copy. Save locally under data/raw, which is ignored by Git.
Record rough hand-labeled times, part IDs and visibility in a separate local note.
Use the offline ingest command from README. No media upload is part of this slice.

## Later dataset and metrics

Use clean ordered, deliberate omission, deliberate reorder, occlusion and camera
movement scenarios, targeting two repeats each. These are plans, not collected
sessions. Keep calibration and final evaluation recordings separate; do not tune
and report success on the same clip. Labels need session, event interval, action,
part, visibility and independently known deliberate omissions. Match predictions
to labels one-to-one with a predeclared temporal tolerance.

Report precision TP/(TP+FP), recall TP/(TP+FN), part-assignment accuracy and unresolved
rate; evidence coverage separately from actual omission detection; order errors and
false alarms in clean sessions; and incorrect observed promotion during bad-quality
intervals. Every rate includes numerator, denominator and n. A zero denominator is
null/undefined. Report upload-inclusive/exclusive latency definitions, call count,
actual cost, model/API version, algorithm/threshold/config hash and run date.
Small mock-panel samples do not establish general accuracy.

Compare motion-only, part association and quality gates. Voice would be a separate
future ablation. Evaluate 1/5/10 fps against the original timeline; 5 fps is only an
initial candidate, 1 fps may miss fast movement, and interpolation restores no lost
visual evidence. Record negative findings as well as improvements.

## Evidence available in this delivery

Unit masks and ffprobe fixtures are explicitly SYNTHETIC. Integration tests create
short local test-pattern videos with nonzero PTS and reordered encoded packets;
they test decoded presentation timing, file validation and manifest hashes. They
are not mock-panel recordings or segmentation quality evaluations. The optional
parser diagnostic reproduces a contract failure using a documented synthetic
codec vector. No real SAM request or real-media mask/ID quality, event
precision/recall, part assignment, actual cost/latency or user-feedback study has run.
The separate Round 2 synthetic estimator results are recorded below.

## Exact first 30-second recording checklist

Before recording: use only the permitted civil mock panel, fix the phone on a
tripod, label 4–10 parts, use steady lighting, keep the handle/socket visible and
exclude faces, personal papers and sensitive hardware. Do not move the camera.

| Media seconds | Action / exact spoken metadata |
|---|---|
| 0–5 | Hold the panel view. Say: "Mock panel, session one, tool [name], part [ID]." |
| 5–15 | Perform visible tool motion on the named part, then pause. |
| 15–20 | Briefly occlude the tool. |
| 20–25 | Reveal it and perform another visible movement. |
| 25–30 | Stop and say: "End of recording." |

Keep the original MP4/MOV and PTS unchanged; add separate hand labels for part,
visibility and motion windows. Spoken metadata is for the recording only; no voice
integration is implemented. Real-media input was absent this round, so this checklist
was supplied and useful offline work continued without claiming real ingestion.

Round 2 measured the independent synthetic estimator in docs/RISK_GATE.md. Full-set
precision is 10/11, recall 10/13. Clean detections are 10/10; the three quality-withheld
positive cases remain false negatives in the full denominator. Incorrect stable-camera
metadata causes the one false positive. Labels do not change when detector thresholds
change. The report records fixed-threshold 1/5/10 fps outcomes and a real-media gate
of >=8/10 clean true candidates, precision >=0.90 including negatives, and zero
witnessed promotion during annotated bad-quality intervals. That real gate is NOT_RUN.
