# Demo assets

The film and every file it is made from, as of round 18. `artifacts/`, `data/raw/`, `demo-video/out/`
and `demo-video/public/witness/` are git-ignored: those files exist on the operator machine only and
are never committed. The film is authored in `demo-video/src/beats.ts`, and `docs/DEMO_SCRIPT.md` is
generated from it by `npm run script-doc`. The claim the film may make is set by D030 and D031.

## The submission film

`demo-video/out/witness_demo_final.mp4` is the submission file: 180.000 s, 5400 frames, 1920x1080 h264
with AAC audio (180.011 s), rendered by `npm run render` in round 18. The round-17 cut is kept beside it
as `witness_demo_r17.mp4`, the fallback. `witness_demo_v1.mp4` to `witness_demo_v3.mp4` are superseded
intermediates; the 181.60 s round-16 cut was deleted in round 18.

## Beat by beat

| Beat | On screen | Source |
|---|---|---|
| 1 | The small mono mark and the question, set alone; the bolt B-roll for its 8 s, captioned "intended use case — not a measurement" | `demo-video/public/brand/witness-logo-mono.svg`; `data/raw/demo_bolts_v1_clean.mp4`, source 0–8 s, no audio |
| 2 | The skipped clip's event log as ten procedure parts filling in the order they were seen, its first evidence still, the three checks and the report's two findings | `artifacts/sessions/58bb85e4-77eb-4297-882a-aac467a05bca/events.json` and its `evidence/evidence-1.png`; `artifacts/real_skipped_05/findings.json`; `data/procedures/panel_boxes_v1.json` |
| 3 | The hash chain as three points and two drawn links with the full values, the recompute rule, and the limit: local hashes, no trust anchor | `artifacts/real_skipped_05/manifest.json`, `artifacts/real_skipped_05/manifest.sha256` |
| 4 | 25, 10, 1 and 3 on a baseline with the caveat that all 25 cases are synthetic | `docs/RISK_GATE.md` |
| 5 | The geometry-only run as stated figures, clean and skipped side by side; no picture and no model output | `docs/REAL_MEDIA.md` (Round 7 measurement) |
| 6 | A threshold drawn at 2.0, two bars stopping at 1.97 and 1.93, the frames where extraction stopped | `docs/REAL_MEDIA.md` (Round 8 measurement) |
| 7 | The model overlays of both clips at one crop; sam-3.1, 78 anchors at one call each, USD 0.1950; the calibration limit, which stays to the end | `artifacts/overlays/model_clean_anchor48.png`, `artifacts/overlays/model_skipped_anchor28.png`; `docs/REAL_MEDIA.md` (Model-produced events); `docs/STATUS.md` |
| 8 | The claim, one slow drawn rule, the full gradient mark | `demo-video/public/brand/witness-logo.svg` |

Each beat's narration is `demo-video/public/voiceover/beat-NN.mp3`, measured in `MANIFEST.md`. The
render plays a loudness-normalised copy (loudnorm, -16 LUFS, 100 ms fades) and never edits a clip.

## How the files reach the film

`demo-video/sync-assets.mjs` copies the files above into `demo-video/public/witness/`, masking the
repository and home paths in every text copy, cuts the bolt excerpt and measures each voiceover clip
against `MANIFEST.md`. Before a frame renders, the composition refuses a drawn string that contains a
user path, a clip longer than its slot, subtitles that are not the narration word for word, slots that
do not fill 5400 frames, and a mark whose gradient is not the film's ramp.

## The mark

`demo-video/public/brand/witness-logo.svg` and `witness-logo-mono.svg` are hand-written vectors, traced
in round 18 from the operator's raster reference, which is not in the repository: four rods and five
joints, rod width 6.1% of the mark's width, joints 2.5 to 2.7 times the rod half-width with the lower
pair larger, a gradient from #01112F at the base to #194C9E at the crown, and a #3B80DE rim. The film
draws the mark from these files.
