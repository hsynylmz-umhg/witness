# Voiceover manifest

Generated 2026-10-28. Eight clips, one per beat of `docs/DEMO_SCRIPT.md`. The spoken text is
identical to the script's spoken column.

| Beat | File | Duration (s) | Slot (s) | Fits |
|---:|---|---:|---:|:--|
| 1 | `beat-01.mp3` | 13.04 | 15 | yes |
| 2 | `beat-02.mp3` | 18.73 | 25 | yes |
| 3 | `beat-03.mp3` | 17.08 | 20 | yes |
| 4 | `beat-04.mp3` | 13.04 | 25 | yes |
| 5 | `beat-05.mp3` | 29.15 | 40 | yes |
| 6 | `beat-06.mp3` | 19.41 | 25 | yes |
| 7 | `beat-07.mp3` | 9.01 | 20 | yes |
| 8 | `beat-08.mp3` | 6.09 | 10 | yes |

**Total audio 125.54 s in a 180 s cut**, leaving 54.46 s of silence distributed across the beats.
No beat is over its slot, so no script words are shortened.

Durations above were measured by parsing the MP3 frame headers, so they are exact, not estimates.
`docs/DEMO_VO.md` carries the earlier 150-wpm estimates for comparison; the measured values are the
ones that matter.

Format: MPEG-1 Layer III, constant bitrate, 8 000 bytes per second of audio. That is why two clips
of identical duration have identical file sizes — not a duplicated file.

Source of truth for the spoken text remains `docs/DEMO_SCRIPT.md`. If the script changes, these
clips are regenerated, never patched.
