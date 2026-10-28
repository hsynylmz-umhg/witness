# Voiceover

The eight clips `beat-01.mp3` to `beat-08.mp3` are synthesised speech, generated on 2026-10-28
from the spoken column of `docs/DEMO_SCRIPT.md`; the operator did not record any audio. The
narration is in English, which is not the operator's first language, and that is why it was
synthesised. No field audio exists, and the bolt footage's own sound is muted in the film.

The durations in `MANIFEST.md` were measured from the MP3 frame headers. `sync-assets.mjs`
measures every clip again with `ffprobe` on each render and fails on more than 0.5 s of drift
from the manifest, or on a clip longer than its beat, so a stale manifest cannot shift a cut.
