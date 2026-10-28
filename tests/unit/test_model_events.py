"""SYNTHETIC anchoring and overlay checks for the model event path; no network, no media."""

import numpy as np

from witness.model.events import anchor_samples, reanchor
from witness.model.overlay import GLYPHS, SCALE, label

BOXES = {"BOX_01": (0, 0, 100, 100), "BOX_02": (400, 0, 500, 100), "BOX_03": (0, 400, 100, 500)}


def test_SYNTHETIC_anchors_fall_on_the_first_sample_of_each_five_second_step():
    samples = [(index * 6, index * 0.2 + 0.01) for index in range(1205)]
    anchors = anchor_samples(samples)
    assert len(anchors) == 49  # a 240.8 s plan: 0 s to 240 s every 5 s
    assert all(time_s >= 5 * number for number, (_, time_s) in enumerate(anchors))
    assert all(time_s - 5 * number < 0.2 for number, (_, time_s) in enumerate(anchors))


def test_SYNTHETIC_drift_within_tolerance_is_accepted_and_beyond_it_is_an_anchor_event():
    shifted = {part: (x1 + 12, y1, x2 + 12, y2) for part, (x1, y1, x2, y2) in BOXES.items()}
    accepted, events, drift = reanchor(BOXES, shifted)
    assert accepted == shifted and events == [] and drift["BOX_01"] == 12

    jumped = dict(shifted, BOX_02=(0, 0, 100, 100))  # tolerance is a quarter of 400 px
    accepted, events, _ = reanchor(BOXES, jumped)
    assert accepted["BOX_02"] == BOXES["BOX_02"]
    assert [(event["part_id"], event["kind"]) for event in events] == [("BOX_02", "moved")]


def test_SYNTHETIC_a_box_the_model_misses_keeps_its_mask_and_is_recorded():
    named = {part: box for part, box in BOXES.items() if part != "BOX_03"}
    named["BOX_07"] = (200, 200, 300, 300)
    accepted, events, _ = reanchor(BOXES, named)
    assert accepted == BOXES
    assert sorted((event["part_id"], event["kind"]) for event in events) == [
        ("BOX_03", "missing"),
        ("BOX_07", "new"),
    ]


def test_SYNTHETIC_ten_renders_as_two_digits_and_unassigned_is_legible():
    image = np.zeros((40, 400, 3), dtype=np.uint8)
    label(image, 0, 0, "10 not marked", (255, 255, 255))
    lit = image[SCALE : 6 * SCALE].any(axis=2).any(axis=0)
    first, second = lit[SCALE : 4 * SCALE], lit[5 * SCALE : 8 * SCALE]
    assert first.any() and second.any()  # both glyphs of "10" are drawn
    assert all(character in GLYPHS for character in "unassigned not marked")
