"""Deterministic pencil-mark events for the printed ten-box panel (D029, rule v2, round 7).

Why v2 measures texture: rule v1 (round 6) measured mean luminance, which cannot separate a
pencil from a hand. Both make a box darker. Pencil hatching adds high-frequency structure (dark
strokes, light gaps), while a hand adds a flat, smooth darkening. Gradient energy sees the
difference; mean luminance does not.

The rule below was fixed before either real clip was run through it, and is not changed after.

- Frames are decoded once by ffmpeg as 8-bit gray at 960x540; only planned samples are used.
- Sheet: Otsu threshold on the first sample; the largest 4-connected bright component is the
  sheet. If it covers less than SHEET_MIN_FRACTION of the frame, extraction raises.
- Boxes: the other bright components whose centre lies inside the sheet bounds, whose bounding
  box stays at least BORDER_PX from every frame edge (the sheet sits inside the frame, so an
  edge-touching region is a cut-off sliver, not a box: P-029a), with area between
  BOX_MIN_FRACTION and BOX_MAX_FRACTION of the frame and bounding-box fill of at least
  BOX_MIN_FILL. Anything but exactly columns x rows of them raises.
- Windows: each box mask is eroded by MASK_EROSION_PX and the sheet mask by PAPER_EROSION_PX,
  so no printed outline or sheet edge enters a sample. At 960x540 an outline and its
  anti-aliased halo are at most about 3 px wide, so 4 px clears them (a judgement call).
- Gradient energy of a window = mean absolute first difference, horizontal and vertical, over
  pixel pairs that both lie in the window.
- Texture ratio = box energy / paper energy (the eroded sheet margin, same frame). Exposure gain
  scales both alike, so the ratio cancels exposure drift across a long clip.
- Each box's ratio is normalised by its own baseline: the median over the first BASELINE_S
  seconds. This cancels the printed digit, which is texture that never changes. Smoothed =
  trailing median over SMOOTH_S seconds of the normalised ratio.
- RISE = 2.0: a box is marked only if its smoothed ratio ends at or above twice its baseline.
  Physics: unmarked paper at this scale gives a mean first difference of a few gray levels
  (sensor noise and grain). A graphite stroke is roughly 40-60% of paper luminance, a step of
  tens of gray levels even after downscaling. Hatching repeats that step every few pixels
  across the box, so it adds several times the paper's own energy. A flat hand adds no first
  differences inside itself, only one silhouette edge. "At least double" is the judgement call.
- RELEASE = 1.5, halfway to RISE, is the hysteresis level. The sustained rise is the final run
  of samples at or above RELEASE that reaches the end of the clip. Noise around RISE cannot
  restart it, which was the round-6 onset bug.
- Mark: that run lasts at least PERSIST_S seconds and ends at or above RISE. A hand that crosses
  a box and leaves ends its run before the clip does. Onset = first sample of the run, which
  lags the stroke by up to about half of SMOOTH_S.

Measured limitation: there is no homography. Boxes are located as printed regions in pixels, so
their masks follow perspective; only grid assignment uses order (rows by y, then x). The
residual perspective error is reported as the largest distance between a box centre,
normalised to the union of box bounds, and its ideal grid centre.
Known failure: a textured object (a patterned sleeve) resting on a box for PERSIST_S at the
very end of a clip.
"""

import json
import shutil
import subprocess
import tempfile
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from witness.audit.models import load_procedure
from witness.errors import WitnessError
from witness.evidence.manifest import sha256_file

WIDTH, HEIGHT = 960, 540
SHEET_MIN_FRACTION = 0.05
BOX_MIN_FRACTION = 0.002
BOX_MAX_FRACTION = 0.06
BOX_MIN_FILL = 0.5
BORDER_PX = 2
MASK_EROSION_PX = 4
PAPER_EROSION_PX = 4
BASELINE_S = 1.0
SMOOTH_S = 1.0
RISE = 2.0
RELEASE = 1.5
PERSIST_S = 3.0
RULE = "panel_boxes_rule_v2"


@dataclass(frozen=True)
class Layout:
    paper: np.ndarray
    part_ids: tuple[str, ...]
    masks: tuple[np.ndarray, ...]
    residual: float


def _otsu(gray: np.ndarray) -> int:
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
    below = np.cumsum(hist)
    above = gray.size - below
    first_moment = np.cumsum(hist * np.arange(256))
    with np.errstate(divide="ignore", invalid="ignore"):
        between = (first_moment[-1] * below / gray.size - first_moment) ** 2 / (below * above)
    return int(np.nanargmax(between))


def _components(bright: np.ndarray) -> tuple[np.ndarray, list[int]]:
    height, width = bright.shape
    flat = bright.ravel().tolist()
    labels = [0] * len(flat)
    sizes = [0]
    for start in np.flatnonzero(bright.ravel()).tolist():
        if labels[start]:
            continue
        label = len(sizes)
        labels[start] = label
        queue, count = deque([start]), 0
        while queue:
            pixel = queue.popleft()
            count += 1
            y, x = divmod(pixel, width)
            for neighbour, inside in (
                (pixel - 1, x > 0),
                (pixel + 1, x < width - 1),
                (pixel - width, y > 0),
                (pixel + width, y < height - 1),
            ):
                if inside and flat[neighbour] and not labels[neighbour]:
                    labels[neighbour] = label
                    queue.append(neighbour)
        sizes.append(count)
    return np.array(labels, dtype=np.int32).reshape(height, width), sizes


def _erode(mask: np.ndarray, steps: int) -> np.ndarray:
    for _ in range(steps):
        inner = mask.copy()
        inner[1:] &= mask[:-1]
        inner[:-1] &= mask[1:]
        inner[:, 1:] &= mask[:, :-1]
        inner[:, :-1] &= mask[:, 1:]
        mask = inner
    return mask


def locate_boxes(frame: np.ndarray, sheet_spec: Mapping[str, Any]) -> Layout:
    """Find the sheet and its printed boxes in the first frame, or raise with the reason."""
    columns, rows = int(sheet_spec["columns"]), int(sheet_spec["rows"])
    labels, sizes = _components(frame > _otsu(frame))
    if len(sizes) < 2:
        raise WitnessError("Sheet not found in the first frame: no bright region.")
    sheet_label = max(range(1, len(sizes)), key=sizes.__getitem__)
    if sizes[sheet_label] < SHEET_MIN_FRACTION * frame.size:
        raise WitnessError(
            "Sheet not found in the first frame: the largest bright region covers "
            f"{sizes[sheet_label] / frame.size:.1%}, below {SHEET_MIN_FRACTION:.0%}."
        )
    sheet = labels == sheet_label
    sheet_y, sheet_x = np.nonzero(sheet)
    found = []
    for label, size in enumerate(sizes):
        if label in (0, sheet_label) or not (
            BOX_MIN_FRACTION * frame.size <= size <= BOX_MAX_FRACTION * frame.size
        ):
            continue
        mask = labels == label
        ys, xs = np.nonzero(mask)
        fill = size / ((np.ptp(ys) + 1) * (np.ptp(xs) + 1))
        centre_y, centre_x = ys.mean(), xs.mean()
        inside_frame = (
            min(ys.min(), xs.min()) >= BORDER_PX
            and ys.max() < frame.shape[0] - BORDER_PX
            and xs.max() < frame.shape[1] - BORDER_PX
        )
        if (
            inside_frame
            and fill >= BOX_MIN_FILL
            and sheet_y.min() <= centre_y <= sheet_y.max()
            and sheet_x.min() <= centre_x <= sheet_x.max()
        ):
            found.append((centre_y, centre_x, mask))
    if len(found) != columns * rows:
        raise WitnessError(
            f"Expected {columns * rows} printed boxes inside the sheet, found {len(found)}."
        )
    found.sort(key=lambda item: item[0])
    grid = [
        sorted(found[r * columns : (r + 1) * columns], key=lambda item: item[1])
        for r in range(rows)
    ]
    union = np.logical_or.reduce([item[2] for item in found])
    union_y, union_x = np.nonzero(union)
    by_cell = {
        (round(cell["uv"][0] * columns), round(cell["uv"][1] * rows)): part_id
        for part_id, cell in sheet_spec["cells"].items()
    }
    part_ids, masks, residual = [], [], 0.0
    for row, boxes in enumerate(grid):
        for column, (centre_y, centre_x, mask) in enumerate(boxes):
            part_id = by_cell[(column, row)]
            u0, v0, u1, v1 = sheet_spec["cells"][part_id]["uv"]
            u = (centre_x - union_x.min()) / max(np.ptp(union_x), 1)
            v = (centre_y - union_y.min()) / max(np.ptp(union_y), 1)
            residual = max(residual, float(np.hypot(u - (u0 + u1) / 2, v - (v0 + v1) / 2)))
            eroded = _erode(mask, MASK_EROSION_PX)
            if not eroded.any():
                raise WitnessError(f"Box {part_id} vanishes after outline erosion.")
            part_ids.append(part_id)
            masks.append(eroded)
    paper = _erode(sheet, PAPER_EROSION_PX)
    if not paper.any():
        raise WitnessError("Sheet margin vanishes after edge erosion.")
    return Layout(paper, tuple(part_ids), tuple(masks), residual)


def _gradient_energy(dx: np.ndarray, dy: np.ndarray, mask: np.ndarray) -> float:
    pairs = np.concatenate([dx[mask[:, 1:] & mask[:, :-1]], dy[mask[1:] & mask[:-1]]])
    return float(pairs.mean())


def box_ratios(frame: np.ndarray, layout: Layout) -> np.ndarray:
    """Return each box's gradient energy relative to the paper margin in the same frame."""
    signed = frame.astype(np.int16)
    dx, dy = np.abs(np.diff(signed, axis=1)), np.abs(np.diff(signed, axis=0))
    paper = _gradient_energy(dx, dy, layout.paper)
    if paper <= 0:
        raise WitnessError("Paper margin shows no measurable texture in a sampled frame.")
    return np.array([_gradient_energy(dx, dy, mask) for mask in layout.masks]) / paper


def mark_onsets(times: np.ndarray, ratios: np.ndarray) -> list[int | None]:
    """Return the first sample of each box's sustained texture rise, or None."""
    if len(times) == 0 or times[-1] - times[0] < BASELINE_S + PERSIST_S:
        raise WitnessError("Clip is too short for the baseline and persistence windows.")
    baseline = np.median(ratios[times - times[0] < BASELINE_S], axis=0)
    if np.any(baseline <= 0):
        raise WitnessError("A box has no measurable baseline texture.")
    smoothed = (
        np.array([np.median(ratios[(times <= t) & (times > t - SMOOTH_S)], axis=0) for t in times])
        / baseline
    )
    onsets: list[int | None] = []
    for box in range(ratios.shape[1]):
        below = np.flatnonzero(smoothed[:, box] < RELEASE)
        start = int(below[-1]) + 1 if len(below) else 0
        sustained = smoothed[-1, box] >= RISE and times[-1] - times[start] >= PERSIST_S
        onsets.append(start if sustained else None)
    return onsets


def measure(
    frames: Iterable[tuple[float, np.ndarray]], sheet_spec: Mapping[str, Any]
) -> tuple[Layout, np.ndarray, np.ndarray]:
    """Locate boxes in the first frame, then measure every frame against that layout."""
    layout, times, ratios = None, [], []
    for time_s, frame in frames:
        if layout is None:
            layout = locate_boxes(frame, sheet_spec)
        times.append(time_s)
        ratios.append(box_ratios(frame, layout))
    if layout is None:
        raise WitnessError("No sampled frames were decoded.")
    return layout, np.array(times), np.array(ratios)


def events_from_onsets(
    layout: Layout, times: np.ndarray, onsets: list[int | None]
) -> list[dict[str, Any]]:
    """Order marks by onset and give each the session-local event and evidence ids."""
    marked = sorted((onset, index) for index, onset in enumerate(onsets) if onset is not None)
    return [
        {
            "event_id": f"event-{order}",
            "part_id": layout.part_ids[index],
            "observed_order": order,
            "status": "witnessed",
            "evidence_id": f"evidence-{order}",
            "evidence_path": f"evidence/evidence-{order}.png",
            "timestamp_s": float(times[onset]),
        }
        for order, (onset, index) in enumerate(marked, start=1)
    ]


def _decode(video: Path, wanted: Mapping[int, float], total: int):
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise WitnessError("ffmpeg is not available on PATH.")
    command = [
        executable, "-v", "error", "-i", str(video), "-map", "0:v:0", "-fps_mode", "passthrough",
        "-vf", f"scale={WIDTH}:{HEIGHT},format=gray", "-f", "rawvideo", "pipe:1",
    ]  # fmt: skip
    size = WIDTH * HEIGHT
    index = 0
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        while chunk := process.stdout.read(size):
            if len(chunk) != size:
                raise WitnessError("ffmpeg returned a truncated frame.")
            if index in wanted:
                yield wanted[index], np.frombuffer(chunk, np.uint8).reshape(HEIGHT, WIDTH)
            index += 1
    if process.returncode or index != total:
        raise WitnessError(f"ffmpeg decoded {index} frames, the session timeline records {total}.")


def _write_stills(video: Path, frame_indices: list[int], evidence_dir: Path) -> None:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise WitnessError("ffmpeg is not available on PATH.")
    unique = sorted(set(frame_indices))
    with tempfile.TemporaryDirectory(dir=evidence_dir.parent) as scratch:
        select = "+".join(f"eq(n\\,{index})" for index in unique)
        command = [
            executable, "-v", "error", "-i", str(video), "-map", "0:v:0", "-fps_mode",
            "passthrough", "-vf", f"select={select},scale={WIDTH}:-2",
            str(Path(scratch) / "still-%04d.png"),
        ]  # fmt: skip
        if subprocess.run(command, capture_output=True, check=False).returncode:
            raise WitnessError("ffmpeg could not extract the evidence stills.")
        stills = sorted(Path(scratch).glob("still-*.png"))
        if len(stills) != len(unique):
            raise WitnessError("ffmpeg returned a different number of evidence stills.")
        by_index = dict(zip(unique, stills))
        evidence_dir.mkdir(exist_ok=False)
        for order, index in enumerate(frame_indices, start=1):
            (evidence_dir / f"evidence-{order}.png").write_bytes(by_index[index].read_bytes())


def extract_box_events(session_dir: Path, video: Path, procedure_path: Path) -> dict[str, Any]:
    """Write events.json, box_marks.json and evidence stills for one ingested panel session."""
    session_dir = session_dir.resolve()
    session = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    if (session_dir / "events.json").exists() or (session_dir / "evidence").exists():
        raise WitnessError("This session already has events; they are never overwritten.")
    if sha256_file(video) != session["source_sha256"]:
        raise WitnessError("Video bytes do not match the session's source hash.")
    procedure_document = json.loads(procedure_path.read_text(encoding="utf-8"))
    load_procedure(procedure_document)
    sheet_spec = procedure_document.get("sheet")
    if not isinstance(sheet_spec, Mapping) or not {"columns", "rows", "cells"} <= sheet_spec.keys():
        raise WitnessError("Procedure has no sheet layout with columns, rows and cells.")
    timeline = json.loads((session_dir / "timeline.json").read_text(encoding="utf-8"))
    samples = json.loads((session_dir / "samples.json").read_text(encoding="utf-8"))["samples"]
    wanted = {
        sample["original_frame_index"]: sample["media_time_s"]
        for sample in samples
        if sample["media_time_s"] is not None
    }
    by_time = {time_s: index for index, time_s in wanted.items()}
    layout, times, ratios = measure(_decode(video, wanted, len(timeline["frames"])), sheet_spec)
    onsets = mark_onsets(times, ratios)
    events = events_from_onsets(layout, times, onsets)
    still_frames = []
    for event in events:
        onset_time = event["timestamp_s"]
        settled = times[times >= onset_time + PERSIST_S]
        still_frames.append(by_time[float(settled[0]) if len(settled) else float(times[-1])])
    if events:
        _write_stills(video, still_frames, session_dir / "evidence")
    diagnostics = {
        "rule": RULE,
        "constants": {
            "rise": RISE, "release": RELEASE, "persist_s": PERSIST_S, "baseline_s": BASELINE_S,
            "smooth_s": SMOOTH_S, "mask_erosion_px": MASK_EROSION_PX,
            "paper_erosion_px": PAPER_EROSION_PX, "border_px": BORDER_PX, "width": WIDTH,
            "height": HEIGHT,
        },
        "perspective_residual_uv": layout.residual,
        "samples": len(times),
        "boxes": [],
    }  # fmt: skip
    for box, part_id in enumerate(layout.part_ids):
        onset_s = None if onsets[box] is None else float(times[onsets[box]])
        diagnostics["boxes"].append(
            {
                "part_id": part_id,
                "baseline_ratio": float(np.median(ratios[times - times[0] < BASELINE_S, box])),
                "max_ratio": float(ratios[:, box].max()),
                "final_ratio": float(ratios[-1, box]),
                "onset_frame_index": None if onset_s is None else by_time[onset_s],
                "onset_s": onset_s,
            }
        )
    with (session_dir / "box_marks.json").open("x", encoding="utf-8") as stream:
        json.dump(diagnostics, stream, indent=2)
    with (session_dir / "events.json").open("x", encoding="utf-8") as stream:
        json.dump({"producer": RULE, "events": events}, stream, indent=2)
    return {
        "events": len(events),
        "marked": [event["part_id"] for event in events],
        "perspective_residual_uv": round(layout.residual, 4),
        "samples": len(times),
        "model_integration_status": "NOT_RUN",
    }
