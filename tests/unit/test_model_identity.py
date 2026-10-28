"""SYNTHETIC region sets for the geometric identity rule; no network, no media."""

import json
from pathlib import Path

from witness.model.identity import assign

SHEET = json.loads(
    (Path(__file__).parents[2] / "data/procedures/panel_boxes_v1.json").read_text(encoding="utf-8")
)["sheet"]


def _box(number: int) -> tuple[int, int, int, int]:
    """A SYNTHETIC 1920x1080 view with perspective: the far row is narrower and shorter."""
    column, near = (number - 1) // 2, number % 2 == 1
    if near:
        x0, pitch, y0, height = 100, 340, 700, 220
    else:
        x0, pitch, y0, height = 250, 280, 530, 160
    return x0 + column * pitch + 10, y0, x0 + (column + 1) * pitch - 10, y0 + height


def test_SYNTHETIC_round_13_arrival_order_maps_to_the_sheet_numbering():
    order = [5, 6, 3, 9, 10, 4, 1, 7, 8, 2]
    result = assign([_box(n) for n in order], SHEET)
    assert {part: order[index] for part, index in result.by_part.items()} == {
        f"BOX_{n:02d}": n for n in range(1, 11)
    }
    assert result.unassigned == () and result.collisions == 0 and result.gaps == ()


def test_SYNTHETIC_a_missing_region_is_a_reported_gap():
    result = assign([_box(n) for n in range(1, 11) if n != 7], SHEET)
    assert len(result.by_part) == 9 and result.gaps == ("BOX_07",)
    assert result.unassigned == () and result.collisions == 0


def test_SYNTHETIC_two_regions_on_one_cell_are_one_assignment_and_one_collision():
    boxes = [_box(n) for n in range(1, 11)]
    x1, y1, x2, y2 = _box(6)
    boxes.append((x1 + 40, y1 + 20, x2 + 40, y2 + 20))  # a second, offset claim on box 6
    result = assign(boxes, SHEET)
    # The nearer of the two keeps the cell; the other is counted, never chosen by order.
    assert len(result.by_part) == 10 and result.by_part["BOX_06"] in (5, 10)
    assert result.collisions == 1 and len(result.unassigned) == 1
    assert {result.by_part["BOX_06"], *result.unassigned} == {5, 10}
    assert len(set(result.by_part.values())) == 10


def test_SYNTHETIC_a_region_far_off_the_sheet_is_unassigned_without_raising():
    boxes = [_box(n) for n in range(1, 11)] + [(5000, 5000, 5100, 5100)]
    result = assign(boxes, SHEET)
    assert len(result.by_part) == 10 and result.unassigned == (10,)
    assert {part: index + 1 for part, index in result.by_part.items()} == {
        f"BOX_{n:02d}": n for n in range(1, 11)
    }


def test_SYNTHETIC_an_exact_tie_assigns_nobody_rather_than_choosing_by_order():
    boxes = [_box(n) for n in range(1, 11) if n != 6] + [_box(6), _box(6)]
    result = assign(boxes, SHEET)
    assert "BOX_06" not in result.by_part and "BOX_06" in result.gaps
    assert result.unassigned == (9, 10) and result.collisions == 1
