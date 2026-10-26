"""Experimental sampling references, preserving source frame identity."""

import math
from dataclasses import dataclass
from fractions import Fraction

from witness.errors import WitnessError
from witness.media.probe import FrameTime


@dataclass(frozen=True)
class SampleReference:
    sample_index: int
    requested_time_s: float | None
    original_frame_index: int
    pts: int | None
    media_time_s: float | None
    quality_flags: tuple[str, ...]


def plan_samples(
    frames: tuple[FrameTime, ...], candidate_fps: float
) -> tuple[SampleReference, ...]:
    """Select the first frame at/after each grid point, once per source frame.

    This plans references only. It does not extract frames or configure a provider.
    Long gaps skip grid points rather than duplicating or interpolating a frame.
    """
    if not math.isfinite(candidate_fps) or candidate_fps <= 0:
        raise WitnessError("Candidate sampling FPS must be finite and positive.")
    rate = Fraction(str(candidate_fps))
    grid_index = 0
    samples: list[SampleReference] = []
    previous: float | None = None
    for frame in frames:
        time_s = frame.media_time_s
        if time_s is None:
            continue
        if not math.isfinite(time_s) or time_s < 0 or (previous is not None and time_s <= previous):
            raise WitnessError("Sampling requires increasing nonnegative media timestamps.")
        previous = time_s
        moment = Fraction(str(time_s))
        if moment < grid_index / rate:
            continue
        flags = list(frame.quality_flags)
        if moment - grid_index / rate > 1 / rate:
            flags.append("sampling_gap")
        samples.append(
            SampleReference(
                sample_index=len(samples),
                requested_time_s=float(grid_index / rate),
                original_frame_index=frame.original_frame_index,
                pts=frame.pts,
                media_time_s=time_s,
                quality_flags=tuple(flags),
            )
        )
        grid_index = math.floor(moment * rate) + 1
    return tuple(samples)


def map_sample_indices(
    frames: tuple[FrameTime, ...],
    original_indices: tuple[int, ...],
) -> tuple[SampleReference, ...]:
    """Map explicitly selected source indices without filling unknown timestamps."""
    by_index = {frame.original_frame_index: frame for frame in frames}
    if len(by_index) != len(frames) or len(set(original_indices)) != len(original_indices):
        raise WitnessError("Source and selected sampling indices must be unique.")
    samples = []
    for sample_index, original_index in enumerate(original_indices):
        if original_index not in by_index:
            raise WitnessError("Selected original frame index is not present in the source.")
        frame = by_index[original_index]
        samples.append(
            SampleReference(
                sample_index,
                None,
                frame.original_frame_index,
                frame.pts,
                frame.media_time_s,
                frame.quality_flags,
            )
        )
    return tuple(samples)
