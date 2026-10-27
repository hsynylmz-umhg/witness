// Copies the demo's source files into public/witness/ so the composition can load them.
// Every path comes from docs/DEMO_ASSETS.md or docs/DEMO_SCRIPT.md; a missing file stops the sync.
// No video is copied: the source clips stay in data/raw/.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

const root = join(import.meta.dirname, "..");
const files = {
  "DEMO_SCRIPT.md": "docs/DEMO_SCRIPT.md",
  "RISK_GATE.md": "docs/RISK_GATE.md",
  "REAL_MEDIA.md": "docs/REAL_MEDIA.md",
  "STATUS.md": "docs/STATUS.md",
  "clean_report.html": "artifacts/real_clean_02/report.html",
  "skipped_report.html": "artifacts/real_skipped_02/report.html",
  "clean_manifest.json": "artifacts/real_clean_02/manifest.json",
  "clean_evidence-1.png": "artifacts/real_clean_02/evidence/evidence-1.png",
  "overlay.png": "artifacts/overlays/real_clean_02_frame-7224.png",
};
const missing = Object.values(files).filter((source) => !existsSync(join(root, source)));
if (missing.length) {
  console.error(`Missing demo assets: ${missing.join(", ")}`);
  process.exit(1);
}
for (const [name, source] of Object.entries(files)) {
  const target = join(import.meta.dirname, "public", "witness", name);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(join(root, source), target);
  console.log(`${source} -> public/witness/${name}`);
}
