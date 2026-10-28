"""Event log from Meta model anchors (D032, D033): the model proposes, the code names and measures.

Rule `model_anchor_rule_v1`, written before the first clip run and not changed after it:

- Anchors: the first planned sample at or after every ANCHOR_S = 5 s of clip time, starting at
  0 s. Only anchors call the model (`sam-3.1`, prompt "printed square box", one image each,
  through the existing spend gate in `witness.adapters.sam_probe`). A 240 s clip is 49 calls.
- Identity: `witness.model.identity.assign` names each anchor's regions (identity v2).
- The measured set is fixed at the first anchor: every box named there is measured; a box
  missing there is a gap, has no baseline and can produce no event.
- Re-anchor, per box: the new region replaces the box's mask only if the same box is named again
  and its centre moved at most ANCHOR_TOLERANCE = a quarter of the smallest distance between two
  accepted box centres (in source pixels, from the current set). Otherwise the old mask stays and
  an anchor event is recorded: `missing` (not named this time), `moved` (beyond the tolerance)
  or `new` (named now, absent from the measured set). An anchor event is never silently
  accepted, and it is never a finding.
- Masks: each region's raster sits at its box's top-left corner in source pixels (60 of 60
  round-13 regions have raster size equal to box size). It is resampled to the 960x540 working
  frame and eroded by perception's MASK_EROSION_PX. The paper reference is the rectangle spanning
  the accepted boxes, minus every box mask dilated by PAPER_EROSION_PX.
- Measure: perception's `box_ratios`, `mark_onsets` and `events_from_onsets` are called
  unchanged (RISE 2.0, RELEASE 1.5, 3 s, 1 s baseline). Between anchors the masks do not move.
- Spend: before every call the shared ledger total is read; the run stops if one more request
  would take it past ROUND_STOP_USD = 1.00. More calls than anchors is a bug and raises.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping
from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np

from witness.adapters.sam_probe import probe_image, send_image
from witness.audit.models import load_procedure
from witness.config import load_settings
from witness.errors import WitnessError
from witness.evidence.manifest import sha256_file
from witness.model.identity import assign
from witness.model.spike import segmentation_candidates
from witness.perception.boxes import (
    HEIGHT,
    MASK_EROSION_PX,
    PAPER_EROSION_PX,
    PERSIST_S,
    WIDTH,
    Layout,
    _decode,
    _erode,
    _write_stills,
    box_ratios,
    events_from_onsets,
    mark_onsets,
)

RULE = "model_anchor_rule_v1"
PROMPT = "printed square box"
ANCHOR_S = 5.0
ROUND_STOP_USD = Decimal("1.00")


def anchor_samples(samples: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """First planned sample at or after each ANCHOR_S boundary; samples sorted by time."""
    anchors, boundary = [], 0.0
    for index, time_s in samples:
        if time_s >= boundary:
            anchors.append((index, time_s))
            boundary = (math.floor(time_s / ANCHOR_S) + 1) * ANCHOR_S
    return anchors


def _centre(box: tuple[int, int, int, int]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def tolerance(boxes: Mapping[str, tuple[int, int, int, int]]) -> float:
    centres = [_centre(box) for box in boxes.values()]
    return min(math.dist(a, b) for i, a in enumerate(centres) for b in centres[i + 1 :]) / 4


def reanchor(
    current: Mapping[str, tuple[int, int, int, int]], named: Mapping[str, tuple[int, int, int, int]]
) -> tuple[dict[str, tuple[int, int, int, int]], list[dict[str, Any]], dict[str, float]]:
    """Apply the per-box acceptance rule; return the accepted set, anchor events and drift."""
    limit = tolerance(current)
    accepted, events, drift = dict(current), [], {}
    for part_id, box in current.items():
        if part_id not in named:
            events.append({"part_id": part_id, "kind": "missing"})
            continue
        moved = math.dist(_centre(box), _centre(named[part_id]))
        drift[part_id] = moved
        if moved <= limit:
            accepted[part_id] = named[part_id]
        else:
            events.append({"part_id": part_id, "kind": "moved", "px": moved, "limit_px": limit})
    events += [{"part_id": part, "kind": "new"} for part in sorted(set(named) - set(current))]
    return accepted, events, drift


def _working_mask(mask) -> np.ndarray:
    """Place a box-sized raster at its box corner, resample to the working frame, erode."""
    full = np.zeros((mask.frame_height, mask.frame_width), dtype=bool)
    x1, y1, x2, y2 = mask.box_xyxy_inclusive
    if mask.raster.shape != (y2 - y1 + 1, x2 - x1 + 1):
        raise WitnessError("A model mask raster does not match its box; placement is unknown.")
    full[y1 : y2 + 1, x1 : x2 + 1] = mask.raster.astype(bool)
    rows = (np.arange(HEIGHT) * mask.frame_height) // HEIGHT
    columns = (np.arange(WIDTH) * mask.frame_width) // WIDTH
    return _erode(full[np.ix_(rows, columns)], MASK_EROSION_PX)


def layout_from(masks: Mapping[str, Any]) -> Layout:
    """A perception Layout whose masks come from the model; registration fields are unused."""
    part_ids = tuple(sorted(masks))
    working = [_working_mask(masks[part]) for part in part_ids]
    union = np.logical_or.reduce(working)
    ys, xs = np.nonzero(union)
    paper = np.zeros_like(union)
    paper[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1] = True
    paper &= ~np.logical_or.reduce([_dilated(mask) for mask in working])
    if not paper.any() or not all(mask.any() for mask in working):
        raise WitnessError("A model mask or the paper reference vanished after erosion.")
    return Layout(paper, part_ids, tuple(working), 0.0, (slice(0, 0), slice(0, 0)), np.empty(0), 0)


def _dilated(mask: np.ndarray) -> np.ndarray:
    # A box mask is eroded by MASK_EROSION_PX; dilate it back past its outline before the paper
    # reference excludes it.
    return ~_erode(~mask, MASK_EROSION_PX + PAPER_EROSION_PX)


def _ledger_total(ledger_root: Path) -> Decimal:
    path = ledger_root / "spend-ledger.json"
    if not path.exists():
        return Decimal(0)
    rows = json.loads(path.read_text(encoding="utf-8"))["requests"]
    return sum(
        (
            Decimal(r["actual_usd"] if r["actual_usd"] is not None else r["reservation_usd"])
            for r in rows
        ),
        Decimal(0),
    )


def _anchor_frames(video: Path, indices: list[int], target: Path) -> list[Path]:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise WitnessError("ffmpeg is not available on PATH.")
    target.mkdir(parents=True, exist_ok=False)
    select = "+".join(f"eq(n\\,{index})" for index in indices)
    command = [
        executable, "-v", "error", "-i", str(video), "-map", "0:v:0", "-fps_mode", "passthrough",
        "-vf", f"select={select}", "-q:v", "2", str(target / "anchor-%03d.jpg"),
    ]  # fmt: skip
    if subprocess.run(command, capture_output=True, check=False).returncode:
        raise WitnessError("ffmpeg could not extract the anchor frames.")
    frames = sorted(target.glob("anchor-*.jpg"))
    if len(frames) != len(indices):
        raise WitnessError("ffmpeg returned a different number of anchor frames.")
    return frames


def extract_model_events(
    session_dir: Path,
    video: Path,
    procedure_path: Path,
    *,
    allow_paid: bool,
    config: Path | None,
    ledger_root: Path,
) -> dict[str, Any]:
    """Write events.json, model_marks.json and evidence stills for one ingested panel session."""
    session_dir = session_dir.resolve()
    session = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    for existing in ("events.json", "evidence", "model"):
        if (session_dir / existing).exists():
            raise WitnessError(f"This session already has {existing}; it is never overwritten.")
    if sha256_file(video) != session["source_sha256"]:
        raise WitnessError("Video bytes do not match the session's source hash.")
    document = json.loads(procedure_path.read_text(encoding="utf-8"))
    load_procedure(document)
    sheet_spec = document["sheet"]
    settings = load_settings(config)
    timeline = json.loads((session_dir / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((session_dir / "samples.json").read_text(encoding="utf-8"))["samples"]
    samples = sorted(
        (
            (s["original_frame_index"], s["media_time_s"])
            for s in plan
            if s["media_time_s"] is not None
        ),
        key=lambda item: item[1],
    )
    anchors = anchor_samples(samples)
    work = session_dir / "model"
    jpegs = _anchor_frames(video, sorted(index for index, _ in anchors), work / "frames")
    by_index = dict(zip(sorted(index for index, _ in anchors), jpegs))

    records, current, current_masks, calls = [], {}, {}, 0
    for number, (frame_index, time_s) in enumerate(anchors):
        if calls >= len(anchors):
            raise WitnessError("More model calls than anchors; the anchoring logic is wrong.")
        spent = _ledger_total(ledger_root)
        if spent + settings.sam.image_usd_per_1000 / 1000 > ROUND_STOP_USD:
            raise WitnessError(f"Round stop: ledger USD {spent} would pass USD {ROUND_STOP_USD}.")
        response: list[bytes] = []
        started = time.monotonic()
        entry = probe_image(
            by_index[frame_index],
            work / f"spend-{session['session_id']}",
            settings=settings,
            allow_paid=allow_paid,
            env_budget=os.environ.get("WITNESS_MAX_SPEND_USD"),
            api_key=os.environ.get("MODEL_API_KEY"),
            ledger_root=ledger_root,
            transport=partial(send_image, prompt=PROMPT, sink=response.append),
            announce=lambda _: None,
        )
        calls += 1
        latency = time.monotonic() - started
        (work / f"anchor-{number:03d}.json").write_bytes(response[0])
        regions = segmentation_candidates(json.loads(response[0])) or ()
        result = assign([m.box_xyxy_inclusive for m in regions], sheet_spec)
        named = {part: regions[i].box_xyxy_inclusive for part, i in result.by_part.items()}
        if number == 0:
            if len(named) < 2:
                raise WitnessError(
                    "The first anchor named fewer than two boxes; nothing to measure."
                )
            current, anchor_events, drift = dict(named), [], {}
            current_masks = {part: regions[i] for part, i in result.by_part.items()}
        else:
            current, anchor_events, drift = reanchor(current, named)
            for part in current:
                if part in named and current[part] == named[part]:
                    current_masks[part] = regions[result.by_part[part]]
        records.append(
            {
                "anchor": number, "frame_index": frame_index, "media_time_s": time_s,
                "latency_s": round(latency, 3), "cost_usd": entry["actual_usd"],
                "regions": len(regions), "named": sorted(named),
                "unassigned": len(result.unassigned),
                "collisions": result.collisions, "gaps": list(result.gaps),
                "drift_px": {part: round(px, 1) for part, px in drift.items()},
                "anchor_events": anchor_events,
                "layout": layout_from(current_masks),
            }
        )  # fmt: skip
        print(
            f"anchor {number:02d} t={time_s:7.2f} s regions {len(regions)} named {len(named)} "
            f"unassigned {len(result.unassigned)} collisions {result.collisions} "
            f"events {len(anchor_events)} {latency:.1f} s USD {entry['actual_usd']}",
            flush=True,
        )

    wanted = dict(samples)
    anchor_times = [record["media_time_s"] for record in records]
    times, ratios = [], []
    for time_s, frame in _decode(video, wanted, len(timeline["frames"])):
        layout = records[int(np.searchsorted(anchor_times, time_s, side="right")) - 1]["layout"]
        times.append(time_s)
        ratios.append(box_ratios(frame, layout))
    times, ratios = np.array(times), np.array(ratios)
    layout = records[0]["layout"]
    onsets = mark_onsets(times, ratios)
    events = events_from_onsets(layout, times, onsets)
    by_time = {time_s: index for index, time_s in samples}
    stills = []
    for event in events:
        settled = times[times >= event["timestamp_s"] + PERSIST_S]
        stills.append(by_time[float(settled[0]) if len(settled) else float(times[-1])])
    if events:
        _write_stills(video, stills, session_dir / "evidence")
    for record in records:
        del record["layout"]
    sidecar = {
        "rule": RULE,
        "identity_rule": "identity v2 (witness.model.identity)",
        "model": "sam-3.1",
        "prompt": PROMPT,
        "anchor_s": ANCHOR_S,
        "round_stop_usd": str(ROUND_STOP_USD),
        "calls": calls,
        "anchors": records,
        "boxes": [
            {
                "part_id": part_id,
                "baseline_ratio": float(np.median(ratios[times - times[0] < 1.0, box])),
                "final_ratio": float(ratios[-1, box]),
                "onset_s": None if onsets[box] is None else float(times[onsets[box]]),
                "marked": onsets[box] is not None,
            }
            for box, part_id in enumerate(layout.part_ids)
        ],
    }
    with (session_dir / "model_marks.json").open("x", encoding="utf-8") as stream:
        json.dump(sidecar, stream, indent=2)
    with (session_dir / "events.json").open("x", encoding="utf-8") as stream:
        json.dump({"producer": RULE, "events": events}, stream, indent=2)
    return {
        "calls": calls,
        "anchor_events": sum(len(r["anchor_events"]) for r in records),
        "unassigned": sum(r["unassigned"] for r in records),
        "collisions": sum(r["collisions"] for r in records),
        "max_drift_px": max((max(r["drift_px"].values(), default=0) for r in records), default=0),
        "measured": list(layout.part_ids),
        "marked": [event["part_id"] for event in events],
        "ledger_usd": str(_ledger_total(ledger_root)),
        "model_integration_status": "SPIKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--procedure", type=Path, required=True)
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    try:
        summary = extract_model_events(
            args.session, args.video, args.procedure, allow_paid=args.allow_paid,
            config=args.config, ledger_root=root / "artifacts",
        )  # fmt: skip
    except WitnessError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
