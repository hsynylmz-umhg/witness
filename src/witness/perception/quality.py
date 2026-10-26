"""Pure continuity checks; usable geometry is never an observed action."""

import math
from dataclasses import dataclass
from typing import Literal

from witness.errors import WitnessError
from witness.perception.features import MaskFeatures, axis_delta_deg


@dataclass(frozen=True)
class PairQuality:
    usable_for_axis_change: bool
    delta_axis_deg: float | None
    quality_flags: tuple[str, ...]


def assess_axis_pair(
    previous: MaskFeatures,
    current: MaskFeatures,
    *,
    previous_time_s: float,
    current_time_s: float,
    max_gap_s: float,
    identity_continuity_confirmed: bool = False,
    visibility: Literal["visible", "occluded", "out_of_frame", "unknown"] = "unknown",
    reference_area_px: float | None = None,
    min_area_ratio: float = 0.4,
    timestamp_quality_flags: tuple[str, ...] = (),
) -> PairQuality:
    """Reject missing visibility/identity, timestamp gaps and possible occlusion.

    Area loss is a heuristic, not an occlusion detector. A caller must still
    establish visibility and track continuity independently after disappearance.
    """
    if (
        not all(math.isfinite(value) for value in (previous_time_s, current_time_s, max_gap_s))
        or previous_time_s < 0
        or current_time_s < 0
        or max_gap_s <= 0
        or not 0 < min_area_ratio <= 1
    ):
        raise WitnessError("Invalid continuity thresholds or timestamps.")
    if reference_area_px is not None and (
        not math.isfinite(reference_area_px) or reference_area_px <= 0
    ):
        raise WitnessError("Reference mask area must be finite and positive.")
    if visibility not in {"visible", "occluded", "out_of_frame", "unknown"}:
        raise WitnessError("Unknown visibility state.")
    flags = list(timestamp_quality_flags)
    if not previous.shape_valid:
        flags.append("previous_shape_invalid")
        flags.extend(f"previous_{flag}" for flag in previous.quality_flags)
    if not current.shape_valid:
        flags.append("current_shape_invalid")
        flags.extend(f"current_{flag}" for flag in current.quality_flags)
    if not identity_continuity_confirmed:
        flags.append("identity_unresolved")
    if visibility != "visible":
        flags.append(visibility if visibility != "unknown" else "visibility_unknown")
    elapsed = current_time_s - previous_time_s
    if elapsed <= 0:
        flags.append("nonincreasing_timestamp")
    elif elapsed > max_gap_s:
        flags.append("timestamp_gap")
    if reference_area_px is not None and current.area_px / reference_area_px < min_area_ratio:
        flags.append("possible_occlusion")
    delta = None
    if previous.axis_deg_mod180 is None or current.axis_deg_mod180 is None:
        flags.append("axis_unavailable")
    elif not flags:
        delta = axis_delta_deg(previous.axis_deg_mod180, current.axis_deg_mod180)
        if delta is None:
            flags.append("axis_direction_ambiguous")
    return PairQuality(not flags, delta if not flags else None, tuple(dict.fromkeys(flags)))
