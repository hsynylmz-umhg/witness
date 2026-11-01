# Voiceover manifest

Generated 2026-10-28, corrected 2026-10-28 after measuring with ffprobe. Eight clips, one per beat of
`docs/DEMO_SCRIPT.md`. The spoken text is identical to the script's spoken column.

| Beat | File | Duration (s) | Slot (s) | Fits |
|---:|---|---:|---:|:--|
| 1 | `beat-01.mp3` | 12.97 | 14.400 | yes |
| 2 | `beat-02.mp3` | 18.65 | 20.067 | yes |
| 3 | `beat-03.mp3` | 17.02 | 18.433 | yes |
| 4 | `beat-04.mp3` | 12.97 | 16.600 | yes — designed hold |
| 5 | `beat-05.mp3` | 29.08 | 30.500 | yes |
| 6 | `beat-06.mp3` | 19.35 | 21.767 | yes — designed freeze |
| 7 | `beat-07.mp3` | 21.54 | 22.967 | yes |
| 8 | `beat-08.mp3` | 6.01 | 7.433 | yes |

**Total audio 137.59 s in a 152.17 s cut**, leaving 14.57 s of silence. Of that, 6.04 s is the two
designed pressure points, beat 4's hold and beat 6's freeze; the other 8.53 s is a breath of about
1.4 s after each of the six other clips. No beat is over its slot and no word is shortened. The clips are not shipped; these are the measured durations the slots derive from.

Since round 20 the slots are derived in `demo-video/src/beats.ts`: each is its clip plus a 1.400 s
breath, rounded up to a frame, except beat 4's hold (3.600 s) and beat 6's freeze (2.400 s). The
total above is the sum of this table's duration column; quote it from here, nowhere else.

All eight durations were re-measured with `ffprobe` in rounds 16 and 17. Clips 1–6 and 8 had been listed
from MP3 frame-header counts, 0.06–0.08 s longer than ffprobe reports; the table now carries the
ffprobe values. Beat 7's frame-header count is 21.60 s against ffprobe's 21.54 s — the difference is
encoder delay, and ffprobe is the number that governs synchronisation. The render re-measures every clip with
ffprobe and refuses a manifest that is off by more than 0.5 s.

Format: MPEG-1 Layer III, constant bitrate. Source of truth for the spoken text remains
`docs/DEMO_SCRIPT.md`. If the script changes, these clips are regenerated, never patched.
