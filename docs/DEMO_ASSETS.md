# Demo assets

Raw material for the three-minute video, not the video itself. Every path below exists on the
operator machine as of round 11, unless it is marked `MISSING`. `artifacts/` and `data/raw/` are
git-ignored, so those files are local only and are never committed. The claim the video may make
is set by D030 and D031: verification of an event log, with the perception extractor shown as a
measured demonstration, misses included. The `_02` assets come from rule v2 (tag `r7`).
The round-8 `_03` reports were built over an absent event log after rule v3 refused both clips;
they were deleted in round 9 and `build` now refuses a session without `events.json`.

| Asset | Path | What it shows |
|---|---|---|
| Bolt B-roll (intended use case) | `data/raw/demo_bolts_v1_clean.mp4`, source 0-8 s; `data/raw/demo_bolts_v2_skipped.mp4` is filed but not in the film | Beat 1 of `witness_demo_v2.mp4`: a driver turning screw 1 of a numbered row, no clip audio, with "intended use case — not a measurement" burned in for the whole segment. Intended use case, not a measurement: no procedure, extraction or findings exist for these clips |
| Voiceover | `demo-video/public/voiceover/beat-01.mp3` to `beat-08.mp3`, `MANIFEST.md` | One clip per beat, loudness-normalised at render time (loudnorm, -16 LUFS integrated) with 100 ms fades; each starts at its beat's first frame |
| Source clips | `data/raw/real_panel_v1_clean.mp4`, `data/raw/real_panel_v1_skipped.mp4` | The permitted mock panel being marked, one clean run and one with a skip and a swap |
| Answer key | `docs/REAL_MEDIA.md` (sections up to "Measured files") | The expected outcome, committed before any measurement |
| Sheet detected, boxes labelled | `artifacts/overlays/real_clean_02_frame-7224.png` | Last frame (original frame index 7224) of session `34630bce-f60f-42ac-aedf-f01fd9cdb064`, drawn by `scripts/overlay_still.py`: sheet bounds in blue, the ten box windows located in frame 0, green for the nine marked and red for BOX_09, matching the clean report. The windows sit offset from the boxes because the sheet drifted after frame 0 (round 8) |
| A confirmed mark | `artifacts/real_clean_02/evidence/evidence-1.png` | BOX_01 hatched, about 3 s after its 5.6 s onset |
| A failure, on camera | `artifacts/real_skipped_02/evidence/evidence-10.png` | Boxes 6, 9 and 10 still blank after events were already claimed for 9 and 10 |
| Report, clean clip | `artifacts/real_clean_02/report.html` | One `skipped` finding (BOX_09), evidence stills, record and report hashes |
| Report, skipped clip | `artifacts/real_skipped_02/report.html` | Three order findings, BOX_03 correct and BOX_06/BOX_09 spurious |
| Hash chain | `artifacts/real_clean_02/manifest.json`, `artifacts/real_clean_02/manifest.sha256` | The hashes a viewer can recompute from the output bytes |
| Risk-gate table | `docs/RISK_GATE.md` | 25 SYNTHETIC cases, TP/FP/FN and the labelling audit |
| Real versus key, side by side | `docs/REAL_MEDIA.md` ("Round 7 measurement") | Expected, found, onset times and why each miss happened |
| Round comparison | `artifacts/real_clean_01/report.html` | The round-6 brightness rule on the same clip, for a before/after shot |
| A loud refusal | `docs/REAL_MEDIA.md` ("Round 8 measurement") | Rule v3 stopping at frame 1558 / 1733 instead of placing masks on an ambiguous registration, with the drift profile |
