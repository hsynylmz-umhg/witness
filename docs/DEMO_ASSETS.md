# Demo assets

The film and every file it is made from, as of round 20. `artifacts/`, `data/raw/`, `demo-video/out/`
and `demo-video/public/witness/` are git-ignored: those files exist on the operator machine only and
are never committed. The film is authored in `demo-video/src/beats.ts`, and `docs/DEMO_SCRIPT.md` is
generated from it by `npm run script-doc`. The claim the film may make is set by D030 and D031.

Every name written on screen resolves in the pushed repository; anything that does not ship is
described, not named. On screen the footage is "clean clip · 0–8 s", the still is "still 1 · BOX_01",
the overlays are "clean clip · anchors" and "skipped clip · anchors", and the only paths are in `docs/`.

## The submission film

`demo-video/out/witness_demo_final.mp4` is the submission file: 152.167 s, 4565 frames, 1920x1080 h264
with AAC audio (152.171 s), rendered by `npm run render` in round 20. The earlier cuts are kept beside it
as fallbacks: `witness_demo_r19.mp4` (163.800 s), `witness_demo_r18.mp4` and `witness_demo_r17.mp4`
(both 180.000 s). `witness_demo_v1.mp4` to `witness_demo_v3.mp4` are superseded intermediates.

Each slot is its narration clip plus a 1.400 s breath, rounded up to a frame, except beat 4's hold
(3.600 s) and beat 6's freeze (2.400 s): 432 · 602 · 553 · 498 · 915 · 653 · 689 · 223 frames.

## Beat by beat

| Beat | On screen | Source |
|---|---|---|
| 1 | The mono mark, one type step up, and the question written over 40 frames above the spine; from 4.6 s to 12.6 s the artefact frame holds the bolt B-roll, captioned as an intended use case, not a measurement | `demo-video/public/brand/witness-logo-mono.svg`; `data/raw/demo_bolts_v1_clean.mp4`, source 0–8 s, no audio |
| 2 | The question, two type steps down, heads the skipped clip's event log: ten procedure parts filling in the order seen, still 1 in the artefact frame, the three checks and the report's two findings | `artifacts/sessions/58bb85e4-77eb-4297-882a-aac467a05bca/events.json` and its `evidence/evidence-1.png`; `artifacts/real_skipped_05/findings.json`; `data/procedures/panel_boxes_v1.json` |
| 3 | Three points on the spine with the full record hash, report hash and manifest.sha256; the recompute rule; the limit; one line quoting the report's skipped finding. The report page itself is not shown: at a size the frame allows its text would be 5.7 px high | `artifacts/real_skipped_05/manifest.json`, `manifest.sha256`, `findings.json` |
| 4 | 25, 10, 1 and 3 on the spine as a baseline, with the caveat that all 25 cases are synthetic; then a hold | `docs/RISK_GATE.md` |
| 5 | The geometry-only run as stated figures, clean and skipped side by side under the spine as a section rule; no picture and no model output | `docs/REAL_MEDIA.md` (Round 7 measurement) |
| 6 | The cause outline opens into the chart frame; the spine is the axis; the threshold at 2.0, bars stopping at 1.97 and 1.93, the frames where extraction stopped; then a freeze | `docs/REAL_MEDIA.md` (Round 8 measurement) |
| 7 | The chart frame becomes the overlay station: the model overlays of both clips at one crop, clean then skipped, each a cut; sam-3.1, 78 anchors at one call each, USD 0.1950; the calibration limit, which stays to the end | `artifacts/overlays/model_clean_anchor48.png`, `artifacts/overlays/model_skipped_anchor28.png`; `docs/REAL_MEDIA.md` (Model-produced events); `docs/STATUS.md` |
| 8 | The claim above the spine as the closing rule; the stroke-only gradient mark with five joints of one construction; a slow rule | `demo-video/public/brand/witness-logo-mono.svg` geometry, rims from `witness-logo.svg` |

Each beat's narration is `demo-video/public/voiceover/beat-NN.mp3`, measured in `MANIFEST.md`. The
render plays a loudness-normalised copy (loudnorm, -16 LUFS, 100 ms fades) and never edits a clip.
Subtitles are the spoken words: each cue starts at its first word's start in the rendered audio.

## How the files reach the film

`demo-video/sync-assets.mjs` copies the files above into `demo-video/public/witness/`, masking the
repository and home paths in every text copy, cuts the bolt excerpt and measures each voiceover clip
against `MANIFEST.md`. The artefact frame has one occupant at every frame (`occupantAt` in `beats.ts`),
which changes on a single declared frame with its caption. Before a frame renders, the composition
refuses a drawn string that contains a user path, a slot shorter than its clip plus 1.400 s (or than its
clip, for beats 4 and 6), subtitles that are not the narration word for word, slots that do not fill
4565 frames, an artefact frame with no occupant or two, or occupant changes under 12 frames apart, and a
mark whose gradient is not the film's ramp.

## The mark

`demo-video/public/brand/witness-logo.svg` and `witness-logo-mono.svg` are hand-written vectors, traced
in round 18 from the operator's raster reference, which is not in the repository: four rods and five
joints, rod width 6.1% of the mark's width, joints 2.5 to 2.7 times the rod half-width with the lower
pair larger, a gradient from #01112F at the base to #194C9E at the crown, and a #3B80DE rim. The film
draws the opening mark from the mono file at a drawn height of 120 px (the xl type step) and the closing
mark stroke-only from the same geometry, on a ground (#050B1A) that is off the mark's ramp.
