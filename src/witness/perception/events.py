"""Pure image-plane rotation/stop candidates over quality-qualified track rows."""

import math
from collections import deque
from dataclasses import dataclass
from statistics import median
from typing import Literal

from witness.config import DetectorConfig, validate_detector_config
from witness.perception.features import MaskFeatures
from witness.perception.quality import assess_axis_pair


@dataclass(frozen=True)
class TrackSample:
    session_id: str
    track_id: str
    original_frame_index: int
    timestamp_s: float | None
    features: MaskFeatures
    visibility: Literal["visible", "occluded", "out_of_frame", "unknown"]
    camera_stable: bool | None
    identity_confirmed: bool
    quality_flags: tuple[str, ...] = ()
    data_origin: Literal["real", "synthetic", "cached_real"] = "synthetic"


@dataclass(frozen=True)
class MotionEvent:
    event_id: str
    session_id: str
    track_id: str
    start_s: float
    end_s: float
    start_frame_index: int
    end_frame_index: int
    delta_axis_deg: float
    status: Literal["witnessed", "inferred", "unwitnessed-tail"]
    quality_flags: tuple[str, ...]
    data_origin: str
    action_type: str = "image_plane_motion_candidate"
    algorithm_version: str = "rotation_stop_v1"


def detect_events(
    track: tuple[TrackSample, ...], config: DetectorConfig
) -> tuple[MotionEvent, ...]:
    """Accumulate usable |axis deltas| and require a qualified stationary tail.

    All experiment thresholds are passed explicitly from configuration. Any bad
    frame, identity/session change or timestamp gap breaks continuity. A completed
    event cannot cross that break or be retroactively upgraded by later frames.
    witnessed is a qualified visual candidate, never proof of tightening or torque.
    """
    validate_detector_config(config)
    events: list[MotionEvent] = []
    previous: TrackSample | None = None
    start: TrackSample | None = None
    last_motion: TrackSample | None = None
    accumulated = 0.0
    calm_count = 0
    calm_since: float | None = None
    areas: deque[int] = deque(maxlen=config.area_history_samples)

    def reached_threshold() -> bool:
        return accumulated + config.numeric_tolerance_deg >= config.min_rotation_deg

    def close(status: str, flags: tuple[str, ...]) -> None:
        nonlocal start, last_motion, accumulated, calm_count, calm_since
        if start is not None and last_motion is not None:
            events.append(
                MotionEvent(
                    event_id=f"motion_{len(events):04d}",
                    session_id=start.session_id,
                    track_id=start.track_id,
                    start_s=start.timestamp_s,
                    end_s=last_motion.timestamp_s,
                    start_frame_index=start.original_frame_index,
                    end_frame_index=last_motion.original_frame_index,
                    delta_axis_deg=accumulated,
                    status=status,
                    quality_flags=flags,
                    data_origin=start.data_origin,
                )
            )
        start, last_motion, accumulated, calm_count, calm_since = None, None, 0.0, 0, None

    for sample in track:
        flags = list(sample.quality_flags)
        time_s = sample.timestamp_s
        if time_s is None or not math.isfinite(time_s) or time_s < 0:
            flags.append("timestamp_unavailable")
        if not sample.features.shape_valid:
            flags.append("shape_invalid")
        if sample.visibility != "visible":
            flags.append(sample.visibility)
        if sample.camera_stable is not True:
            flags.append("camera_unstable_or_unknown")
        if not sample.identity_confirmed:
            flags.append("identity_unresolved")
        if previous is not None and (
            sample.session_id != previous.session_id
            or sample.track_id != previous.track_id
            or sample.data_origin != previous.data_origin
        ):
            flags.append("identity_or_session_change")
        if not flags and previous is not None:
            quality = assess_axis_pair(
                previous.features,
                sample.features,
                previous_time_s=previous.timestamp_s,
                current_time_s=time_s,
                max_gap_s=config.max_gap_seconds,
                identity_continuity_confirmed=True,
                visibility=sample.visibility,
                reference_area_px=median(areas) if areas else None,
                min_area_ratio=config.min_area_ratio,
                timestamp_quality_flags=previous.quality_flags + sample.quality_flags,
            )
            flags.extend(quality.quality_flags)
            if (
                quality.delta_axis_deg is not None
                and abs(quality.delta_axis_deg) > config.max_axis_step_deg
            ):
                flags.append("axis_step_exceeds_continuity_limit")
        if flags:
            if start is not None:
                close("unwitnessed-tail" if reached_threshold() else "inferred", tuple(flags))
            previous = None
            areas.clear()
            continue
        if previous is None:
            previous = sample
            areas.append(sample.features.area_px)
            continue
        delta = abs(quality.delta_axis_deg)
        displacement = math.dist(previous.features.centroid_xy, sample.features.centroid_xy)
        if start is not None and time_s - start.timestamp_s > config.max_event_seconds:
            close("unwitnessed-tail" if reached_threshold() else "inferred", ("event_timeout",))
        if delta >= config.movement_delta_deg:
            if start is None:
                start = previous
            accumulated += delta
            last_motion = sample
            calm_count, calm_since = 0, None
        elif start is not None:
            if delta <= config.stop_delta_deg and displacement <= config.stop_centroid_px:
                calm_count += 1
                if calm_since is None:
                    calm_since = previous.timestamp_s
                if calm_count >= config.min_stop_samples and time_s - calm_since >= (
                    config.min_stop_seconds - config.numeric_tolerance_deg
                ):
                    if reached_threshold():
                        last_motion = sample
                        close("witnessed", ())
                    else:
                        start, last_motion, accumulated, calm_count, calm_since = (
                            None,
                            None,
                            0.0,
                            0,
                            None,
                        )
            else:
                calm_count, calm_since = 0, None
        previous = sample
        areas.append(sample.features.area_px)
    if start is not None:
        close("unwitnessed-tail" if reached_threshold() else "inferred", ("end_without_stop",))
    return tuple(events)
