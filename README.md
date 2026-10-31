# WITNESS

Licensed under the Apache License, Version 2.0 — see LICENSE.

## What this is

WITNESS reads an event log of what happened during a fixed-camera assembly procedure and turns
it into findings: coverage gaps, out-of-order steps and undocumented parts. Every finding carries
an evidence id or it does not exist, except a `skipped` finding, which records that no evidence
was supplied for a step and asks for human review. The report's hash
chain is recomputed from the output bytes, so anyone holding the files can check it.

## What is proven, and where the number lives

| Claim | Value | Source |
|---|---|---|
| Risk gate | 25 labelled cases: 10 TP, 1 FP, 3 FN | `docs/RISK_GATE.md` |
| Test suite | 147 passed | `docs/STATUS.md` |
| Hash chain | recomputes from the output bytes | `tests/integration/test_offline_pipeline.py` |
| Real footage, deterministic extractor | refused at registration on both clips: correlation peak ratio 1.97 and 1.93, against a required 2.0 | `docs/REAL_MEDIA.md` |
| Real footage, Meta model | `RUN`: `sam-3.1` regions, named by geometry and judged by the same texture rule, produced event logs matching the key on both clips; 78 calls, USD 0.1950 | `docs/REAL_MEDIA.md` |

## What is not proven

All 25 risk-gate cases are synthetic. The real footage is one scene, one camera and one lighting
condition, and on it the deterministic extractor disagreed with the answer key: an earlier rule
missed and invented marks, and the final rule refused rather than guess. The model path agrees
with the key on both clips, but its identity rule was calibrated on six frames from these same
two clips, so that agreement is a demonstration on known footage, not independent validation.
Two clips are a demonstration, not a generalisation. Nothing here measures torque, tightening quality, assembly
correctness or flight readiness, and the local hashes are not a signature: without an external
trust anchor they do not stop someone rewriting the files and the manifest together.

## Run it

From the repository root in PowerShell, with the project environment in `.venv`
(`uv sync --locked` creates it) and FFmpeg 8 on `PATH`:

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe scripts/run_risk_gate.py
.venv/Scripts/python.exe -m witness ingest data/raw/real_panel_v1_clean.mp4 --data-origin real
.venv/Scripts/python.exe -m witness build --session artifacts/sessions/SESSION_ID --procedure data/procedures/panel_boxes_v1.json --out artifacts/report
```

The first two need no media. The real clips are not in the repository. `ingest` prints the new
session id, which replaces `SESSION_ID`. `build` refuses a session that has no `events.json`,
because a missing log is not the same as an empty one.

On macOS and Linux the interpreter is `.venv/bin/python` instead of `.venv/Scripts/python.exe`; the
commands are otherwise the same. The two real clips under `data/raw/` are the operator's private
footage and are not shipped. A fresh clone can run the test suite and the risk gate, which are offline
and synthetic (the ffmpeg-marked tests also need FFmpeg on `PATH`); it cannot run `ingest` or `build` on
the real clips, and it cannot re-render the demo film, which needs those clips and the local report
folders under `artifacts/`.

## Repo map

- `.claude/`: local development tooling; nothing under it ships (credits in `docs/CREDITS.md`)
- `artifacts/`: local sessions, reports and overlay stills; git-ignored
- `config/`: default limits for ingest and sampling
- `data/`: procedures; `data/raw/` holds local footage and is git-ignored
- `demo-video/`: the Remotion project that renders the demo film
- `docs/`: rules, decisions, status and every measured number
- `scripts/`: risk gate, workspace validator and the overlay still writer
- `src/`: the `witness` package: ingest, sampling, perception, audit and reports
- `tests/`: offline unit and integration tests, with fixtures named `SYNTHETIC_`

## Third-party tools

Three MIT-licensed agent skills (ponytail, hallmark and humanizer) were used while writing this
code and its documents. They are listed with their sources in `docs/CREDITS.md`.
They are development aids: none of them runs in the pipeline, and none of their output ships as
product code.

## The demo

`witness_demo_final.mp4`, 152.2 s (4565 frames); `docs/DEMO_SCRIPT.md` is its script.
