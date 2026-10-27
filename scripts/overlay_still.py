"""Diagnostic still: the located sheet and box windows drawn on one frame of a panel session.

Demo raw material, not a product feature: `build` never calls this, and it changes nothing in
the session. Box windows come from `locate_boxes` on the session's first sample, exactly as the
extractor located them; they are not moved to the drawn frame, so sheet drift shows as offset.
Marked (green) / unmarked (red) is read from the session's box_marks.json when present;
without it every window is yellow.
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

from witness.evidence.manifest import sha256_file
from witness.perception.boxes import HEIGHT, WIDTH, locate_boxes

DIGITS = {  # 3x5 bitmaps, rows top to bottom
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111",
    "3": "111001111001111", "4": "101101111001001", "5": "111100111001111",
    "6": "111100111101111", "7": "111001001001001", "8": "111101111101111",
    "9": "111101111001111",
}  # fmt: skip
MARKED, UNMARKED, UNKNOWN, SHEET = (40, 200, 60), (230, 40, 40), (240, 200, 0), (40, 120, 255)


def _frame(video: Path, index: int, pixel_format: str, channels: int) -> np.ndarray:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        sys.exit("ffmpeg is not available on PATH.")
    command = [
        ffmpeg, "-v", "error", "-i", str(video), "-map", "0:v:0", "-fps_mode", "passthrough",
        "-vf", f"select=eq(n\\,{index}),scale={WIDTH}:{HEIGHT},format={pixel_format}",
        "-frames:v", "1", "-f", "rawvideo", "pipe:1",
    ]  # fmt: skip
    data = subprocess.run(command, capture_output=True, check=False).stdout
    if len(data) != WIDTH * HEIGHT * channels:
        sys.exit(f"ffmpeg did not return frame {index}.")
    return np.frombuffer(data, np.uint8).reshape(HEIGHT, WIDTH, channels).copy()


def _rectangle(image, top, left, bottom, right, colour, width=2):
    image[top : top + width, left : right + 1] = colour
    image[bottom - width + 1 : bottom + 1, left : right + 1] = colour
    image[top : bottom + 1, left : left + width] = colour
    image[top : bottom + 1, right - width + 1 : right + 1] = colour


def _text(image, top, left, text, colour, scale=3):
    for position, character in enumerate(text):
        bitmap = np.array([int(bit) for bit in DIGITS[character]]).reshape(5, 3)
        block = np.kron(bitmap, np.ones((scale, scale), dtype=int)).astype(bool)
        x = left + position * 4 * scale
        image[top : top + 5 * scale, x : x + 3 * scale][block] = colour


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument(
        "--procedure", type=Path, default=Path("data/procedures/panel_boxes_v1.json")
    )
    parser.add_argument("--frame", type=int, required=True, help="original frame index to draw on")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    session = json.loads((args.session / "session.json").read_text(encoding="utf-8"))
    if sha256_file(args.video) != session["source_sha256"]:
        sys.exit("Video bytes do not match the session's source hash.")
    if args.out.exists():
        sys.exit(f"Refusing to overwrite {args.out}.")
    samples = json.loads((args.session / "samples.json").read_text(encoding="utf-8"))["samples"]
    first = next(s["original_frame_index"] for s in samples if s["media_time_s"] is not None)
    sheet_spec = json.loads(args.procedure.read_text(encoding="utf-8"))["sheet"]
    layout = locate_boxes(_frame(args.video, first, "gray", 1)[:, :, 0], sheet_spec)
    marks_path = args.session / "box_marks.json"
    marks = (
        {
            box["part_id"]: box["onset_s"] is not None
            for box in json.loads(marks_path.read_text())["boxes"]
        }
        if marks_path.exists()
        else {}
    )
    image = _frame(args.video, args.frame, "rgb24", 3)
    sheet_rows, sheet_columns = layout.window
    _rectangle(
        image,
        sheet_rows.start,
        sheet_columns.start,
        sheet_rows.stop - 1,
        sheet_columns.stop - 1,
        SHEET,
    )
    for part_id, mask in zip(layout.part_ids, layout.masks):
        ys, xs = np.nonzero(mask)
        colour = UNKNOWN if part_id not in marks else MARKED if marks[part_id] else UNMARKED
        _rectangle(image, ys.min(), xs.min(), ys.max(), xs.max(), colour)
        _text(image, ys.min() + 6, xs.min() + 6, part_id.removeprefix("BOX_"), colour)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(_png(image))
    print(
        json.dumps(
            {"out": str(args.out), "frame": args.frame, "layout_frame": first, "marks": marks}
        )
    )


if __name__ == "__main__":
    main()
