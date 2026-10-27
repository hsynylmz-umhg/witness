"""SYNTHETIC ten-box panel: the pencil-mark extractor without ffmpeg or real media."""

import json
from pathlib import Path

import numpy as np

from witness.perception.boxes import HEIGHT, WIDTH, events_from_onsets, mark_onsets, measure

SHEET = json.loads(
    (Path(__file__).parents[2] / "data/procedures/panel_boxes_v1.json").read_text(encoding="utf-8")
)["sheet"]
FPS = 5
DURATION_S = 30


def _box(column: int, row: int) -> tuple[int, int, int, int]:
    """Interior bounds of a SYNTHETIC box; row 0 is the far row."""
    x0, y0 = 130 + column * 150, 180 + row * 160
    return y0, y0 + 114, x0, x0 + 114


def _part_box(number: int) -> tuple[int, int, int, int]:
    """Numbering read off the real footage: 1 near-left, up each column."""
    return _box((number - 1) // 2, 1 if number % 2 else 0)


def _frames(mark_times: dict[int, float], hand: tuple[int, float, float] | None = None):
    for index in range(DURATION_S * FPS):
        t = index / FPS
        frame = np.full((HEIGHT, WIDTH), 60, np.uint8)
        frame[150:520, 100:860] = 210
        for number in range(1, 11):
            y0, y1, x0, x1 = _part_box(number)
            frame[y0 - 3 : y0, x0 - 3 : x1 + 3] = 30
            frame[y1 : y1 + 3, x0 - 3 : x1 + 3] = 30
            frame[y0:y1, x0 - 3 : x0] = 30
            frame[y0:y1, x1 : x1 + 3] = 30
            if number in mark_times and t >= mark_times[number]:
                frame[y0:y1, x0 : x0 + 46] = 110
        if hand is not None and hand[1] <= t < hand[2]:
            y0, y1, x0, x1 = _part_box(hand[0])
            frame[y0 - 20 : y1 + 20, x0 - 20 : x1 + 20] = 90
        yield t, frame


def _events(mark_times, hand=None):
    layout, times, ratios = measure(_frames(mark_times, hand), SHEET)
    return events_from_onsets(layout, times, mark_onsets(times, ratios))


def test_SYNTHETIC_ten_marked_boxes_emit_ten_ordered_events_with_evidence_ids():
    events = _events({number: 2.0 * number for number in range(1, 11)})
    assert [event["part_id"] for event in events] == [f"BOX_{n:02d}" for n in range(1, 11)]
    assert all(event["evidence_id"] and event["evidence_path"] for event in events)
    timestamps = [event["timestamp_s"] for event in events]
    assert timestamps == sorted(timestamps) and len(set(timestamps)) == 10


def test_SYNTHETIC_unmarked_box_six_is_the_only_missing_event():
    events = _events({number: 2.0 * number for number in range(1, 11) if number != 6})
    assert len(events) == 9
    assert {f"BOX_{n:02d}" for n in range(1, 11)} - {e["part_id"] for e in events} == {"BOX_06"}


def test_SYNTHETIC_hand_crossing_a_box_and_leaving_emits_no_event():
    events = _events({1: 2.0}, hand=(3, 5.0, 8.0))
    assert [event["part_id"] for event in events] == ["BOX_01"]
