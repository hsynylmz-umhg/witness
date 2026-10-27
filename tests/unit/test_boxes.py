"""SYNTHETIC ten-box panel: the pencil-mark extractor without ffmpeg or real media."""

import json
from pathlib import Path

import numpy as np
import pytest

from witness.errors import WitnessError
from witness.perception import boxes
from witness.perception.boxes import (
    HEIGHT,
    WIDTH,
    events_from_onsets,
    locate_boxes,
    mark_onsets,
    measure,
)

SHEET = json.loads(
    (Path(__file__).parents[2] / "data/procedures/panel_boxes_v1.json").read_text(encoding="utf-8")
)["sheet"]
FPS = 5
DURATION_S = 30
ROWS, COLUMNS = np.mgrid[0:HEIGHT, 0:WIDTH]
HATCH = (ROWS + COLUMNS) % 8 == 0


def _box(column: int, row: int) -> tuple[int, int, int, int]:
    """Interior bounds of a SYNTHETIC box; row 0 is the far row."""
    x0, y0 = 130 + column * 150, 180 + row * 160
    return y0, y0 + 114, x0, x0 + 114


def _part_box(number: int) -> tuple[int, int, int, int]:
    """Numbering read off the real footage: 1 near-left, up each column."""
    return _box((number - 1) // 2, 1 if number % 2 else 0)


def _frames(mark_times: dict[int, float], flat=(), slide=(DURATION_S, 0, 0)):
    """Light diagonal hatching marks (about 4% darker); flat darkenings stand in for a hand.

    slide = (from_s, dy, dx): the whole sheet moves by (dy, dx) px from from_s on.
    """
    for index in range(DURATION_S * FPS):
        t = index / FPS
        dy, dx = slide[1:] if t >= slide[0] else (0, 0)
        frame = np.full((HEIGHT, WIDTH), 60.0)
        frame[150 + dy : 520 + dy, 100 + dx : 860 + dx] = 210
        for number in range(1, 11):
            y0, y1, x0, x1 = _part_box(number)
            y0, y1, x0, x1 = y0 + dy, y1 + dy, x0 + dx, x1 + dx
            frame[y0 - 3 : y0, x0 - 3 : x1 + 3] = 30
            frame[y1 : y1 + 3, x0 - 3 : x1 + 3] = 30
            frame[y0:y1, x0 - 3 : x0] = 30
            frame[y0:y1, x1 : x1 + 3] = 30
            if number in mark_times and t >= mark_times[number]:
                window = frame[y0:y1, x0:x1]
                window[HATCH[y0:y1, x0:x1]] = 140
        for number, start, end in flat:
            if start <= t < end:
                y0, y1, x0, x1 = _part_box(number)
                frame[y0 - 20 : y1 + 20, x0 - 20 : x1 + 20] = 90
        noise = np.random.default_rng(index).normal(0, 2, frame.shape)
        yield t, np.clip(frame + noise, 0, 255).astype(np.uint8)


def _events(mark_times, flat=(), slide=(DURATION_S, 0, 0)):
    layout, times, ratios, _ = measure(_frames(mark_times, flat, slide), SHEET)
    return events_from_onsets(layout, times, mark_onsets(times, ratios))


def test_SYNTHETIC_ten_marked_boxes_emit_ten_ordered_events_with_evidence_ids():
    events = _events({number: 2.0 * number for number in range(1, 11)})
    assert [event["part_id"] for event in events] == [f"BOX_{n:02d}" for n in range(1, 11)]
    assert all(event["evidence_id"] and event["evidence_path"] for event in events)
    timestamps = [event["timestamp_s"] for event in events]
    assert timestamps == sorted(timestamps) and len(set(timestamps)) == 10
    assert all(0 <= t - 2.0 * n <= 1.0 for n, t in enumerate(timestamps, start=1))


def test_SYNTHETIC_unmarked_box_six_is_the_only_missing_event():
    events = _events({number: 2.0 * number for number in range(1, 11) if number != 6})
    assert len(events) == 9
    assert {f"BOX_{n:02d}" for n in range(1, 11)} - {e["part_id"] for e in events} == {"BOX_06"}


def test_SYNTHETIC_texture_rejects_a_flat_hand_and_accepts_light_hatching():
    # A brightness rule fails both ways here: it misses the 4% hatching on box 1 and reports
    # the flat darkening resting on box 3 until the end of the clip.
    events = _events({1: 2.0}, flat=[(5, 5.0, 8.0), (3, 24.0, DURATION_S)])
    assert [event["part_id"] for event in events] == ["BOX_01"]


def test_SYNTHETIC_masks_follow_a_sheet_that_slides_mid_clip():
    # Fixed first-frame masks lose BOX_04, BOX_09 and BOX_10 here: after the slide they cover
    # outline, gap and the neighbouring box instead of the box they were found on.
    marks = {number: 2.0 * number for number in range(1, 11) if number != 6}
    layout, times, ratios, registration = measure(_frames(marks, slide=(11.0, 6, -60)), SHEET)
    events = events_from_onsets(layout, times, mark_onsets(times, ratios))
    assert [event["part_id"] for event in events] == [f"BOX_{n:02d}" for n in marks]
    assert {tuple(row) for row in registration[:, :2].astype(int)} == {(0, 0), (6, -60)}


def test_SYNTHETIC_region_touching_the_frame_edge_is_not_a_box(monkeypatch):
    # P-029a: a bright sliver cut off by the top edge, inside the sheet's bounds.
    frame = dict(_frames({})).get(0.0)
    frame[:150, 100:860] = 210
    frame[0:40, 400:403] = frame[0:40, 467:470] = frame[37:40, 400:470] = 30
    assert len(locate_boxes(frame, SHEET).part_ids) == 10
    monkeypatch.setattr(boxes, "BORDER_PX", 0)
    with pytest.raises(WitnessError, match="found 11"):
        locate_boxes(frame, SHEET)


@pytest.mark.parametrize("covered", ["noise", "lens cap"])
def test_SYNTHETIC_unreadable_sheet_translation_raises(covered):
    def frames():
        for t, frame in _frames({}):
            if t == 10.0:
                rng = np.random.default_rng(0)
                frame = rng.integers(0, 256, frame.shape, dtype=np.uint8)
                frame = frame if covered == "noise" else np.full_like(frame, 12)
            yield t, frame

    with pytest.raises(boxes.AmbiguousRegistration, match=r"t=10\.000 s") as error:
        measure(frames(), SHEET)
    assert error.value.time_s == 10.0
