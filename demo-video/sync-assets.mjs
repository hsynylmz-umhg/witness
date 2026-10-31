// Prepares public/witness/ for the composition. Run by `npm run render` before every render.
// - Copies the film's data from the current run: the round-15 `_05` skipped-clip report folder, the
//   event log of the session it was built from, and the panel procedure. Text copies mask the
//   repository's absolute path as <repo> and the home folder as <home>; any user path left fails the
//   sync with the file name. The sources themselves are never edited.
// - Copies the two model overlays and the first evidence still, and cuts the silent 8 s bolt excerpt
//   for beat 1 (the source clip stays in data/raw/).
// - Re-measures every voiceover clip with ffprobe, fails on drift against MANIFEST.md (> 0.5 s), then
//   loudness-normalises it (loudnorm, -16 LUFS) with 100 ms fades and records the played durations
//   in audio.json. The slot guard runs in the composition, against src/beats.ts.
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const root = join(import.meta.dirname, "..");
const out = join(import.meta.dirname, "public", "witness");
const voice = join(import.meta.dirname, "public", "voiceover");
export const LEAK = /[A-Za-z]:(\\\\|\\|\/)Users(\\\\|\\|\/)/;
const fail = (message) => {
  console.error(message);
  process.exit(1);
};

const SESSION = "artifacts/sessions/58bb85e4-77eb-4297-882a-aac467a05bca";
const REPORT = "artifacts/real_skipped_05";
const text = {
  "procedure.json": "data/procedures/panel_boxes_v1.json",
  "events.json": `${SESSION}/events.json`,
  "findings.json": `${REPORT}/findings.json`,
  "manifest.json": `${REPORT}/manifest.json`,
  "manifest.sha256": `${REPORT}/manifest.sha256`,
};
const binary = {
  "evidence-1.png": `${SESSION}/evidence/evidence-1.png`,
  "model_clean_anchor48.png": "artifacts/overlays/model_clean_anchor48.png",
  "model_skipped_anchor28.png": "artifacts/overlays/model_skipped_anchor28.png",
};
const BOLTS = "data/raw/demo_bolts_v1_clean.mp4";
const missing = [...Object.values(text), ...Object.values(binary), BOLTS].filter(
  (source) => !existsSync(join(root, source)),
);
if (missing.length) fail(`Missing demo assets: ${missing.join(", ")}`);
mkdirSync(join(out, "voiceover"), { recursive: true });

// The repository root, then the home folder, as plain, forward-slash and JSON-escaped text.
const forms = (path) => [path, path.replaceAll("\\", "/"), path.replaceAll("\\", "\\\\")];
for (const [name, source] of Object.entries(text)) {
  let body = readFileSync(join(root, source), "utf8");
  for (const form of forms(root)) body = body.replaceAll(form, "<repo>");
  for (const form of forms(homedir())) body = body.replaceAll(form, "<home>");
  if (LEAK.test(body)) fail(`Absolute user path left in ${source} after masking.`);
  writeFileSync(join(out, name), body);
  console.log(`${source} -> public/witness/${name} (masked)`);
}
for (const [name, source] of Object.entries(binary)) {
  writeFileSync(join(out, name), readFileSync(join(root, source)));
  console.log(`${source} -> public/witness/${name}`);
}

// Beat 1 B-roll: source seconds 0-8, video only, constant 30 fps.
execFileSync("ffmpeg", [
  "-v", "error", "-y", "-ss", "0", "-t", "8", "-i", join(root, BOLTS), "-an",
  "-vf", "scale=1920:1080,fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
  join(out, "bolts_beat1.mp4"),
]);
console.log(`${BOLTS} 0-8 s, no audio -> public/witness/bolts_beat1.mp4`);

const duration = (file) =>
  Number(
    execFileSync("ffprobe", [
      "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file,
    ]).toString(),
  );
const manifest = Object.fromEntries(
  readFileSync(join(voice, "MANIFEST.md"), "utf8")
    .split(/\r?\n/)
    .filter((line) => /^\| ?\d+ \|/.test(line))
    .map((line) => {
      const cells = line.split("|").map((cell) => cell.trim());
      return [Number(cells[1]), Number(cells[3])];
    }),
);
const played = {};
for (const beat of Object.keys(manifest).map(Number)) {
  const name = `beat-${String(beat).padStart(2, "0")}`;
  const source = join(voice, `${name}.mp3`);
  if (!existsSync(source)) fail(`Beat ${beat}: ${name}.mp3 is missing.`);
  const measured = duration(source);
  if (Math.abs(measured - manifest[beat]) > 0.5) {
    fail(`Beat ${beat}: ffprobe measures ${measured.toFixed(3)} s, MANIFEST.md says ${manifest[beat]} s.`);
  }
  const target = join(out, "voiceover", `${name}.wav`);
  execFileSync("ffmpeg", [
    "-v", "error", "-y", "-i", source, "-af",
    `loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.1,afade=t=out:st=${(measured - 0.1).toFixed(3)}:d=0.1`,
    "-ar", "44100", "-ac", "1", target,
  ]);
  played[beat] = duration(target);
  console.log(`beat ${beat}: mp3 ${measured.toFixed(3)} s (manifest ${manifest[beat]}), played ${played[beat].toFixed(3)} s`);
}
writeFileSync(join(out, "audio.json"), JSON.stringify(played, null, 2));
