# Demo assets

Raw material for the three-minute video, not the video itself. Every path below exists on the
operator machine as of round 7, unless it is marked `MISSING`. `artifacts/` and `data/raw/` are
git-ignored, so those files are local only and are never committed. The claim the video may make
is set by D030: verification of an event log, with the perception extractor shown as a measured
demonstration, misses included.

| Asset | Path | What it shows |
|---|---|---|
| Source clips | `data/raw/real_panel_v1_clean.mp4`, `data/raw/real_panel_v1_skipped.mp4` | The permitted mock panel being marked, one clean run and one with a skip and a swap |
| Answer key | `docs/REAL_MEDIA.md` (sections up to "Measured files") | The expected outcome, committed before any measurement |
| Sheet detected, boxes labelled | `MISSING` | No overlay frame is produced; the pipeline stores box masks only in memory |
| A confirmed mark | `artifacts/real_clean_02/evidence/evidence-1.png` | BOX_01 hatched, about 3 s after its 5.6 s onset |
| A failure, on camera | `artifacts/real_skipped_02/evidence/evidence-10.png` | Boxes 6, 9 and 10 still blank after events were already claimed for 9 and 10 |
| Report, clean clip | `artifacts/real_clean_02/report.html` | One `skipped` finding (BOX_09), evidence stills, record and report hashes |
| Report, skipped clip | `artifacts/real_skipped_02/report.html` | Three order findings, BOX_03 correct and BOX_06/BOX_09 spurious |
| Hash chain | `artifacts/real_clean_02/manifest.json`, `artifacts/real_clean_02/manifest.sha256` | The hashes a viewer can recompute from the output bytes |
| Risk-gate table | `docs/RISK_GATE.md` | 25 SYNTHETIC cases, TP/FP/FN and the labelling audit |
| Real versus key, side by side | `docs/REAL_MEDIA.md` ("Round 7 measurement") | Expected, found, onset times and why each miss happened |
| Round comparison | `artifacts/real_clean_01/report.html` | The round-6 brightness rule on the same clip, for a before/after shot |
