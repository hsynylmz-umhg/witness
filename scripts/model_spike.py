"""Round-13 spike: does a Meta segmentation model (SAM 3.1) find the ten printed boxes?

One paid image request per frame, through the existing gate in `witness.adapters.sam_probe`
(WITNESS_MAX_SPEND_USD, --allow-paid, a configured cap, operator-confirmed credits, the shared
spend ledger, no retry). The model is a candidate generator, never an authority (D032): its
regions are saved and drawn, and nothing here writes an event log or a finding.

Fixed before the first call, not edited after a result is seen:

- Prompt text: "printed square box". Model: sam-3.1, the adapter's only model.
- Frames (original frame index; first, middle, last of each clip, outside the marking):
  real_panel_v1_clean.mp4 30, 3613, 7224; real_panel_v1_skipped.mp4 30, 2155, 4307.
- A region is plausible when it lies inside the sheet and covers one printed box; the count
  expected per frame is the procedure's sheet columns x rows (10).

Go/no-go (round-13 prompt, B4):

- Q1, frames with 10 plausible regions: pass >= 5 of 6; marginal 3-4 of 6; fail <= 2 of 6.
- Q1, regions land on the printed boxes (eye check, overlay PNG): pass no systematic offset;
  marginal small offset, correctable by a global shift; fail wrong regions or scattered.
- Cost per frame: pass <= USD 0.05; marginal <= USD 0.20; fail > USD 0.20.
- Latency per frame: pass <= 10 s; marginal <= 30 s; fail > 30 s.

Outputs under artifacts/spike/ (git-ignored): <clip>_f<idx>.jpg (the frame sent),
<clip>_f<idx>_masks.json (the response bytes, unmodified), <clip>_f<idx>_overlay.png and a
<clip>_f<idx>_spend/ folder holding that request's spend.json.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from functools import partial
from pathlib import Path

from scripts.overlay_still import _frame, _png, _rectangle, _text
from witness.adapters.sam_probe import probe_image, send_image
from witness.config import load_settings
from witness.errors import WitnessError
from witness.model.spike import segmentation_candidates
from witness.perception.boxes import HEIGHT, WIDTH

PROMPT = "printed square box"
ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = (255, 140, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--clip", type=Path, required=True)
    parser.add_argument("--procedure", type=Path, required=True)
    parser.add_argument("--frame", type=int, required=True, help="original frame index")
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    sheet = json.loads(args.procedure.read_text(encoding="utf-8"))["sheet"]
    expected = int(sheet["columns"]) * int(sheet["rows"])
    out = ROOT / "artifacts" / "spike"
    stem = f"{args.clip.stem}_f{args.frame}"
    image, masks_path = out / f"{stem}.jpg", out / f"{stem}_masks.json"
    if masks_path.exists():
        sys.exit(f"{masks_path} already holds a paid result; it is never overwritten.")
    out.mkdir(parents=True, exist_ok=True)
    if not image.exists():
        command = [
            shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-i", str(args.clip),
            "-vf", f"select=eq(n\\,{args.frame})", "-fps_mode", "passthrough",
            "-frames:v", "1", "-q:v", "2", str(image),
        ]  # fmt: skip
        if subprocess.run(command, check=False).returncode or not image.exists():
            sys.exit(f"ffmpeg could not extract frame {args.frame} of {args.clip}.")
    print(f"frame {args.clip.name} #{args.frame} -> {image.relative_to(ROOT).as_posix()}")

    response: list[bytes] = []
    started = time.monotonic()
    try:
        entry = probe_image(
            image,
            out / f"{stem}_spend",
            settings=load_settings(args.config),
            allow_paid=args.allow_paid,
            env_budget=os.environ.get("WITNESS_MAX_SPEND_USD"),
            api_key=os.environ.get("MODEL_API_KEY"),
            ledger_root=ROOT / "artifacts",
            transport=partial(send_image, prompt=PROMPT, sink=response.append),
        )
    except WitnessError as error:
        print(f"refused or failed: {error}")
        return 2
    latency = time.monotonic() - started
    masks_path.write_bytes(response[0])
    candidates = segmentation_candidates(json.loads(response[0]))
    found = "no parsable segmentation text" if candidates is None else f"{len(candidates)}"
    print(
        f"model {entry['model']}; latency {latency:.2f} s; billed 1 image; "
        f"cost USD {entry['actual_usd']} (spend ledger); regions {found} of {expected}"
    )
    if candidates:
        overlay = _frame(args.clip, args.frame, "rgb24", 3)
        for mask in candidates:
            sx, sy = WIDTH / mask.frame_width, HEIGHT / mask.frame_height
            x1, y1, x2, y2 = mask.box_xyxy_inclusive
            x1, x2, y1, y2 = round(x1 * sx), round(x2 * sx), round(y1 * sy), round(y2 * sy)
            _rectangle(overlay, y1, x1, y2, x2, CANDIDATE)
            _text(overlay, y1 + 4, x1 + 4, str(mask.provider_object_id), CANDIDATE)
        (out / f"{stem}_overlay.png").write_bytes(_png(overlay))
    return 0


if __name__ == "__main__":
    sys.exit(main())
