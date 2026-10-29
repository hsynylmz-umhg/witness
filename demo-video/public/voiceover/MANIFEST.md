# Voiceover manifest

Generated 2026-10-28, corrected 2026-10-28 after measuring with ffprobe. Eight clips, one per beat of
`docs/DEMO_SCRIPT.md`. The spoken text is identical to the script's spoken column.

| Beat | File | Duration (s) | Slot (s) | Fits |
|---:|---|---:|---:|:--|
| 1 | `beat-01.mp3` | 12.97 | 15 | yes |
| 2 | `beat-02.mp3` | 18.65 | 25 | yes |
| 3 | `beat-03.mp3` | 17.02 | 20 | yes |
| 4 | `beat-04.mp3` | 12.97 | 25 | yes |
| 5 | `beat-05.mp3` | 29.08 | 40 | yes |
| 6 | `beat-06.mp3` | 19.35 | 25 | yes |
| 7 | `beat-07.mp3` | **21.54** | **21.60** | yes — slot widened in round 16 |
| 8 | `beat-08.mp3` | 6.01 | 10 | yes |

**Total audio 137.60 s in a 181.60 s cut**, leaving 44.00 s of silence distributed across the beats.
No beat is over its slot, so no script words are shortened.

Beat 7 was re-synthesised in round 15 after the script changed, and its slot was widened from 20 s to
21.60 s in round 16 so the narration is not clipped. Beat 7 measures 21.54 s under ffprobe; the slot
carries 0.06 s of slack so the clip cannot brush the next cut. The cut therefore runs 181.60 s and is
retimed to 180 s before submission.

All eight durations were re-measured with `ffprobe` in round 16. Clips 1–6 and 8 had been listed
from MP3 frame-header counts, 0.06–0.08 s longer than ffprobe reports; the table now carries the
ffprobe values. Beat 7's frame-header count is 21.60 s against ffprobe's 21.54 s — the difference is
encoder delay, and ffprobe is the number that governs synchronisation. The render re-measures every clip with
ffprobe and refuses a manifest that is off by more than 0.5 s.

Format: MPEG-1 Layer III, constant bitrate. Source of truth for the spoken text remains
`docs/DEMO_SCRIPT.md`. If the script changes, these clips are regenerated, never patched.
