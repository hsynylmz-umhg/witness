# Voiceover manifest

Generated 2026-10-28, corrected 2026-10-28 after measuring with ffprobe. Eight clips, one per beat of
`docs/DEMO_SCRIPT.md`. The spoken text is identical to the script's spoken column.

| Beat | File | Duration (s) | Slot (s) | Fits |
|---:|---|---:|---:|:--|
| 1 | `beat-01.mp3` | 12.97 | 15 | yes |
| 2 | `beat-02.mp3` | 18.65 | 25 | yes |
| 3 | `beat-03.mp3` | 17.02 | 20 | yes |
| 4 | `beat-04.mp3` | 12.97 | 21.40 | yes — 3.60 s of silence moved to beat 7 in round 17 |
| 5 | `beat-05.mp3` | 29.08 | 40 | yes |
| 6 | `beat-06.mp3` | 19.35 | 25 | yes |
| 7 | `beat-07.mp3` | 21.54 | 23.60 | yes — slot widened in rounds 16–17 |
| 8 | `beat-08.mp3` | 6.01 | 10 | yes |

**Total audio 137.59 s in a 180.00 s cut**, leaving 42.41 s of silence distributed across the beats.
No beat is over its slot, so no script words are shortened.

Beat 7 was re-synthesised in round 15 after the script changed. Its slot was widened to 21.60 s in
round 16 and to 23.60 s in round 17, taking 3.60 s from the silence after beat 4's narration, so every
clip has at least 2.0 s of slack and the cut is exactly 180.00 s. The total above is the sum of this
table's duration column; quote it from here, nowhere else.

All eight durations were re-measured with `ffprobe` in rounds 16 and 17. Clips 1–6 and 8 had been listed
from MP3 frame-header counts, 0.06–0.08 s longer than ffprobe reports; the table now carries the
ffprobe values. Beat 7's frame-header count is 21.60 s against ffprobe's 21.54 s — the difference is
encoder delay, and ffprobe is the number that governs synchronisation. The render re-measures every clip with
ffprobe and refuses a manifest that is off by more than 0.5 s.

Format: MPEG-1 Layer III, constant bitrate. Source of truth for the spoken text remains
`docs/DEMO_SCRIPT.md`. If the script changes, these clips are regenerated, never patched.
