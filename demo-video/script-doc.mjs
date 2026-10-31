// Dev script, never run by the render: regenerates docs/DEMO_SCRIPT.md from src/beats.ts, where the
// film is authored. Run with `npm run script-doc` after any change to beats.ts (Node strips the types).
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { BEATS, FPS, TOTAL_FRAMES, endOf, startOf } from "./src/beats.ts";

const clock = (frame) => {
  const seconds = frame / FPS;
  const whole = Math.floor(seconds);
  const tenth = Math.round((seconds - whole) * 10);
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}${tenth ? `.${tenth}` : ""}`;
};
const cell = (value) => value.replaceAll("|", "\\|");

const rows = BEATS.map((beat) => {
  const start = startOf(beat.number);
  const end = endOf(beat.number);
  return `| ${beat.number} | ${clock(start)}–${clock(end)} | ${(beat.frames / FPS).toFixed(3)} (${beat.frames}) | ${cell(beat.onScreen)} | "${cell(beat.spoken)}" | ${beat.sources.join(", ")} |`;
});

const doc = `# Demo script — three minutes

Generated from \`demo-video/src/beats.ts\` by \`npm run script-doc\` (run in \`demo-video/\`). The film is
authored in that file; this is its reading copy, and the render never reads it. The claim follows D030
and D031: witness verifies an event log against a procedure and links every finding to evidence and a
recomputable hash chain. It does not claim to detect pencil marks reliably from pixels. Every spoken
number names its source. Assets are listed in \`docs/DEMO_ASSETS.md\`.

| # | Time | Seconds (frames) | On screen | Spoken | Sources |
|---|---|---:|---|---|---|
${rows.join("\n")}

Total: ${(TOTAL_FRAMES / FPS).toFixed(3)} seconds, ${TOTAL_FRAMES} frames at ${FPS} fps. Each slot is its
clip plus a 1.400 s breath, rounded up to a frame, except the designed hold of beat 4 (3.600 s) and
the freeze of beat 6 (2.400 s).

Not said, on purpose: any detection accuracy beyond the two clips, any model claim beyond the
measured run in beat 7, any test count, and any statement about torque, tightening or assembly
correctness.
`;

writeFileSync(join(import.meta.dirname, "..", "docs", "DEMO_SCRIPT.md"), doc);
console.log(`docs/DEMO_SCRIPT.md written from src/beats.ts: ${BEATS.length} beats, ${TOTAL_FRAMES} frames.`);
