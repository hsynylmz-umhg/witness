"""Diagnostic overlay for one anchor frame: the code's names, never the model's arrival order.

Assigned regions carry their sheet number and the texture decision (`marked` / `not marked`);
regions the identity rule declined are drawn in another colour and labelled `unassigned`.
Rendered at 1280x720 so every label fits inside its box at 720p. Demo material, not a finding.
"""

import argparse
import json
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np

from witness.model.identity import assign
from witness.model.spike import segmentation_candidates

WIDTH, HEIGHT, SCALE = 1280, 720, 3
MARKED, NOT_MARKED, UNASSIGNED = (40, 200, 60), (230, 40, 40), (240, 200, 0)
GLYPHS = {  # 3x5, rows top to bottom
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111",
    "3": "111001111001111", "4": "101101111001001", "5": "111100111001111",
    "6": "111100111101111", "7": "111001001001001", "8": "111101111101111",
    "9": "111101111001111", " ": "000000000000000", "a": "010101111101101",
    "d": "110101101101110", "e": "111100110100111", "g": "011100101101011",
    "i": "111010010010111", "k": "101101110101101", "m": "101111111101101",
    "n": "110101101101101", "o": "010101101101010", "r": "110101110101101",
    "s": "011100010001110", "t": "111010010010010", "u": "101101101101111",
}  # fmt: skip


def _frame(video: Path, index: int) -> np.ndarray:
    command = [
        shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-i", str(video), "-map", "0:v:0",
        "-fps_mode", "passthrough", "-vf", f"select=eq(n\\,{index}),scale={WIDTH}:{HEIGHT}",
        "-frames:v", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1",
    ]  # fmt: skip
    data = subprocess.run(command, capture_output=True, check=False).stdout
    if len(data) != WIDTH * HEIGHT * 3:
        sys.exit(f"ffmpeg did not return frame {index}.")
    return np.frombuffer(data, np.uint8).reshape(HEIGHT, WIDTH, 3).copy()


def _rectangle(image, top, left, bottom, right, colour, width=3):
    image[top : top + width, left : right + 1] = colour
    image[bottom - width + 1 : bottom + 1, left : right + 1] = colour
    image[top : bottom + 1, left : left + width] = colour
    image[top : bottom + 1, right - width + 1 : right + 1] = colour


def label(image, top, left, text, colour):
    """Draw text on a dark plate so it reads on paper and on graphite alike."""
    width, height = len(text) * 4 * SCALE + SCALE, 7 * SCALE
    image[top : top + height, left : left + width] = (15, 20, 30)
    for position, character in enumerate(text):
        bitmap = np.array([int(bit) for bit in GLYPHS[character]], dtype=bool).reshape(5, 3)
        block = np.kron(bitmap, np.ones((SCALE, SCALE), dtype=bool))
        x = left + SCALE + position * 4 * SCALE
        image[top + SCALE : top + 6 * SCALE, x : x + 3 * SCALE][block] = colour


def _png(image: np.ndarray) -> bytes:
    def chunk(kind: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
        )

    rows = b"".join(b"\x00" + row.tobytes() for row in image)
    header = struct.pack(">IIBBBBB", image.shape[1], image.shape[0], 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--procedure", type=Path, required=True)
    parser.add_argument("--anchor", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        sys.exit(f"Refusing to overwrite {args.out}.")
    sidecar = json.loads((args.session / "model_marks.json").read_text(encoding="utf-8"))
    record = sidecar["anchors"][args.anchor]
    marked = {box["part_id"]: box["marked"] for box in sidecar["boxes"]}
    response = json.loads((args.session / "model" / f"anchor-{args.anchor:03d}.json").read_bytes())
    regions = segmentation_candidates(response) or ()
    sheet = json.loads(args.procedure.read_text(encoding="utf-8"))["sheet"]
    result = assign([region.box_xyxy_inclusive for region in regions], sheet)
    names = {index: part for part, index in result.by_part.items()}
    image = _frame(args.video, record["frame_index"])
    labels = []
    for index, region in enumerate(regions):
        x1, y1, x2, y2 = region.box_xyxy_inclusive
        sx, sy = WIDTH / region.frame_width, HEIGHT / region.frame_height
        box = (
            round(y1 * sy),
            round(x1 * sx),
            min(round(y2 * sy), HEIGHT - 1),
            min(round(x2 * sx), WIDTH - 1),
        )
        if index in names:
            part = names[index]
            state = (
                "unmeasured" if part not in marked else "marked" if marked[part] else "not marked"
            )
            text = f"{int(part[4:])} {state}"
            colour = MARKED if marked.get(part) else NOT_MARKED
        else:
            text, colour = "unassigned", UNASSIGNED
        _rectangle(image, *box, colour)
        labels.append((box[0] + 6, box[1] + 6, text, colour))
    for top, left, text, colour in labels:  # after every outline, so no box hides a label
        label(image, top, left, text, colour)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(_png(image))
    print(
        json.dumps(
            {"out": str(args.out), "anchor": args.anchor, "frame_index": record["frame_index"]}
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
