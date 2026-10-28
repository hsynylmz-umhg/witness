"""Name the model's box regions by geometry: the model proposes, the code names (D032).

Round 13 showed the model returns ten regions per frame in an arbitrary order, so its object
ids are never used as box identities. This rule (identity v2) was written before the first
clip measurement run and is not changed after it.

- Cell centres come from the procedure: the middle of each cell's uv rectangle, where uv spans
  the printed grid as seen by the camera (u left to right, v far row to near row).
- Region centre: the middle of its inclusive pixel box.
- Normalised sheet coordinates: a region's centre relative to the union of the inlier region
  boxes, so (0, 0) is the grid's top-left corner and (1, 1) its bottom-right. Inliers are the
  regions whose centre lies inside Tukey's fences (quartiles +/- 1.5 x interquartile range) in
  both x and y; an off-sheet region therefore cannot stretch the grid. Outliers are still
  matched, and land too far from every cell to be assigned.
- Match: each region goes to its nearest cell centre (Euclidean, in uv). It is kept only if its
  centre lies inside that cell's own uv rectangle: at most half the cell's width from the
  centre in u and half its height in v (0.1 and 0.25 for this procedure). For an even grid that
  rectangle is exactly the set of points nearest that centre, so the maximum distance is the
  procedure's own cell, not a tuned number. Farther regions are unassigned and produce no event.
- Collision: if several regions claim one cell, the nearest keeps it and the rest are
  unassigned and counted. If the two nearest are within TIE = 0.02 uv of each other, nobody
  keeps the cell: the code cannot tell them apart, and it never falls back to arrival order.
- A cell no region claims is a gap. It is reported, never filled.

Revision before the first clip run, stated rather than hidden: identity v1 capped the Euclidean
distance at half the smallest centre spacing (0.1 uv). Applied to the six saved round-13
responses (no new call), all 60 regions chose the correct nearest cell, but 4 exceeded the cap
(0.102 to 0.114, BOX_09 and BOX_10, where the far row is foreshortened and the model's boxes are
whole bounding boxes of skewed squares). The v1 justification was also wrong: a point whose
nearest centre is a cell's is already nearer that cell than any neighbour, so a cap of half the
spacing guaranteed nothing extra. v2 replaces the cap with the cell rectangle above.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

TIE = 0.02


@dataclass(frozen=True)
class Assignment:
    """part_id -> region index, plus everything the rule declined to name."""

    by_part: dict[str, int]
    unassigned: tuple[int, ...]
    collisions: int
    gaps: tuple[str, ...]
    distance: dict[str, float]


def cell_centres(sheet_spec: Mapping[str, Any]) -> dict[str, tuple[float, float]]:
    return {
        part_id: ((cell["uv"][0] + cell["uv"][2]) / 2, (cell["uv"][1] + cell["uv"][3]) / 2)
        for part_id, cell in sheet_spec["cells"].items()
    }


def half_sizes(sheet_spec: Mapping[str, Any]) -> dict[str, tuple[float, float]]:
    return {
        part_id: ((cell["uv"][2] - cell["uv"][0]) / 2, (cell["uv"][3] - cell["uv"][1]) / 2)
        for part_id, cell in sheet_spec["cells"].items()
    }


def _inside_fences(values: np.ndarray) -> np.ndarray:
    q1, q3 = np.percentile(values, [25, 75])
    spread = 1.5 * (q3 - q1)
    return (values >= q1 - spread) & (values <= q3 + spread)


def assign(boxes: Sequence[tuple[int, int, int, int]], sheet_spec: Mapping[str, Any]) -> Assignment:
    """Assign inclusive (x1, y1, x2, y2) pixel boxes to procedure cells; never raises."""
    centres, halves = cell_centres(sheet_spec), half_sizes(sheet_spec)
    if not boxes:
        return Assignment({}, (), 0, tuple(sorted(centres)), {})
    array = np.array(boxes, dtype=float)
    cx, cy = (array[:, 0] + array[:, 2]) / 2, (array[:, 1] + array[:, 3]) / 2
    inliers = _inside_fences(cx) & _inside_fences(cy)
    x0, y0 = array[inliers, 0].min(), array[inliers, 1].min()
    width = max(array[inliers, 2].max() - x0, 1.0)
    height = max(array[inliers, 3].max() - y0, 1.0)
    u, v = (cx - x0) / width, (cy - y0) / height
    claims: dict[str, list[tuple[float, int]]] = {}
    unassigned: list[int] = []
    for index in range(len(boxes)):
        part_id, distance = min(
            (
                (part, float(np.hypot(u[index] - cu, v[index] - cv)))
                for part, (cu, cv) in centres.items()
            ),
            key=lambda item: item[1],
        )
        du, dv = abs(u[index] - centres[part_id][0]), abs(v[index] - centres[part_id][1])
        if du <= halves[part_id][0] and dv <= halves[part_id][1]:
            claims.setdefault(part_id, []).append((distance, index))
        else:
            unassigned.append(index)
    by_part, distances, collisions = {}, {}, 0
    for part_id, claimants in claims.items():
        claimants.sort()
        collisions += len(claimants) - 1
        if len(claimants) > 1 and claimants[1][0] - claimants[0][0] < TIE:
            unassigned.extend(index for _, index in claimants)
            continue
        by_part[part_id], distances[part_id] = claimants[0][1], claimants[0][0]
        unassigned.extend(index for _, index in claimants[1:])
    gaps = tuple(sorted(set(centres) - set(by_part)))
    return Assignment(by_part, tuple(sorted(unassigned)), collisions, gaps, distances)
