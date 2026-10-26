"""Pure geometry in mask raster coordinates, without action or torque claims."""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from witness.errors import WitnessError


@dataclass(frozen=True)
class MaskFeatures:
    area_px: int
    centroid_xy: tuple[float, float] | None
    axis_deg_mod180: float | None
    elongation: float | None
    shape_valid: bool
    quality_flags: tuple[str, ...]


def mask_features(
    mask: NDArray[np.generic] | None,
    *,
    min_pixels: int = 12,
    min_elongation: float = 2.5,
) -> MaskFeatures:
    """Return pixel-center geometry and conservative shape validity.

    Thresholds are experimental. Passing shape checks says nothing about identity,
    camera stability, visibility, part contact, or whether the mask is correct.
    """
    if min_pixels < 2 or not math.isfinite(min_elongation) or min_elongation <= 1:
        raise WitnessError("Invalid experimental mask thresholds.")
    if mask is None:
        return MaskFeatures(0, None, None, None, False, ("missing_mask",))
    array = np.asarray(mask)
    if array.ndim != 2 or 0 in array.shape:
        raise WitnessError("A mask must be a nonempty two-dimensional binary raster.")
    if array.dtype.kind not in "buif" or not np.all((array == 0) | (array == 1)):
        raise WitnessError("A mask must contain only binary values 0 and 1.")
    ys, xs = np.nonzero(array)
    area = len(xs)
    if area == 0:
        return MaskFeatures(0, None, None, None, False, ("empty_mask",))
    centroid = (float(xs.mean()), float(ys.mean()))
    flags: list[str] = []
    if area < min_pixels:
        flags.append("insufficient_pixels")
    if (
        np.any(xs == 0)
        or np.any(ys == 0)
        or np.any(xs == array.shape[1] - 1)
        or np.any(ys == array.shape[0] - 1)
    ):
        flags.append("frame_boundary_contact")
    axis = None
    elongation = None
    if area >= 2:
        coordinates = np.column_stack((xs, ys)).astype(np.float64)
        centered = coordinates - np.array(centroid)
        covariance = centered.T @ centered / (area - 1)
        values, vectors = np.linalg.eigh(covariance)
        elongation = float(values[-1] / max(float(values[0]), 1e-12))
        if values[-1] <= 0 or elongation < min_elongation:
            flags.append("ambiguous_axis")
        else:
            axis = math.degrees(math.atan2(vectors[1, -1], vectors[0, -1])) % 180
    return MaskFeatures(area, centroid, axis, elongation, not flags, tuple(flags))


def axis_delta_deg(previous: float, current: float) -> float | None:
    """Shortest undirected-axis change; a 90-degree tie has no known direction.

    Continuity assumes less than 90 degrees of real image-plane motion between
    samples. The two angles alone cannot establish that assumption.
    """
    if not math.isfinite(previous) or not math.isfinite(current):
        raise WitnessError("Axis angles must be finite.")
    delta = (current - previous + 90) % 180 - 90
    return None if math.isclose(abs(delta), 90, abs_tol=1e-9) else delta
