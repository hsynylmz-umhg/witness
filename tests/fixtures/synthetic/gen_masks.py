"""SYNTHETIC mask sequences with independent motion and visibility ground truth."""

from dataclasses import dataclass, replace

import numpy as np

from witness.config import Settings
from witness.media.probe import FrameTime
from witness.media.timeline import plan_samples
from witness.perception.events import TrackSample
from witness.perception.features import mask_features


@dataclass(frozen=True)
class SyntheticSequence:
    name: str
    condition: str
    true_rotation_deg: float
    has_stop: bool
    ground_truth_event: bool
    eligible_clean_case: bool
    track: tuple[TrackSample, ...]


def rectangle_mask(angle_deg: float) -> np.ndarray:
    """Rasterize a centered tool-like rectangle; this is no provider prediction."""
    ys, xs = np.indices((128, 128), dtype=float)
    x, y = xs - 63.5, ys - 63.5
    angle = np.deg2rad(angle_deg)
    along = x * np.cos(angle) + y * np.sin(angle)
    across = -x * np.sin(angle) + y * np.cos(angle)
    return ((np.abs(along) <= 40) & (np.abs(across) <= 4)).astype(np.uint8)


def make_sequence(
    total_deg: float,
    has_stop: bool,
    settings: Settings,
    *,
    condition: str = "clean",
    name: str | None = None,
) -> SyntheticSequence:
    # Generator dimensions/durations define test data, not detector thresholds.
    source_fps = 25
    prelude = np.zeros(10)
    motion = np.linspace(0, total_deg, 51)
    stop = np.full(25, total_deg) if has_stop else np.empty(0)
    angles = np.concatenate((prelude, motion, stop))
    case_name = name or f"SYNTHETIC_{condition}_{total_deg:g}_{'stop' if has_stop else 'no_stop'}"
    rows = []
    for index, angle in enumerate(angles):
        visibility = "visible"
        camera_stable = True
        identity_confirmed = True
        track_id = "tool_0"
        timestamp = index / source_fps
        raster = rectangle_mask(float(angle))
        if condition == "occlusion" and index >= 58:
            raster = None
            visibility = "occluded"
        elif condition == "identity_switch" and index >= 35:
            track_id, identity_confirmed = "tool_2", False
        elif condition == "camera_jitter":
            raster = rectangle_mask(float(12 * np.sin(index)))
            camera_stable = False
        elif condition == "unflagged_camera_rotation":
            # Deliberately wrong camera metadata demonstrates a gate-input limitation.
            camera_stable = True
        if condition == "timestamp_gap" and index >= 35:
            timestamp += 1
        features = mask_features(
            raster,
            min_pixels=settings.detection.min_pixels,
            min_elongation=settings.detection.min_elongation,
        )
        rows.append(
            TrackSample(
                case_name,
                track_id,
                index,
                timestamp,
                features,
                visibility,
                camera_stable,
                identity_confirmed,
                data_origin="synthetic",
            )
        )
    # The authored label rule is fixed by the experiment, independent of detector tuning.
    genuine_motion = total_deg >= 45 and has_stop
    if condition in {"camera_jitter", "unflagged_camera_rotation"}:
        genuine_motion = False
    return SyntheticSequence(
        case_name,
        condition,
        0 if condition in {"camera_jitter", "unflagged_camera_rotation"} else total_deg,
        has_stop,
        genuine_motion,
        condition == "clean",
        tuple(rows),
    )


def generate_sequences(settings: Settings) -> tuple[SyntheticSequence, ...]:
    cases = [
        make_sequence(rotation, stop, settings)
        for rotation in (0, 15, 44, 45, 60, 94, 120)
        for stop in (False, True)
    ]
    for index, rotation in enumerate((45, 60, 94, 120, 60, 94)):
        cases.append(
            make_sequence(rotation, True, settings, name=f"SYNTHETIC_clean_repeat_{index}")
        )
    for condition in ("occlusion", "identity_switch", "camera_jitter", "timestamp_gap"):
        cases.append(make_sequence(94, True, settings, condition=condition))
    cases.append(make_sequence(94, True, settings, condition="unflagged_camera_rotation"))
    return tuple(cases)


def sampled_track(case: SyntheticSequence, fps: float) -> tuple[TrackSample, ...]:
    frames = tuple(
        FrameTime(
            original_frame_index=row.original_frame_index,
            pts=round(row.timestamp_s * 1000),
            best_effort_timestamp=round(row.timestamp_s * 1000),
            media_time_s=row.timestamp_s,
            timestamp_source="pts",
            quality_flags=row.quality_flags,
        )
        for row in case.track
    )
    samples = plan_samples(frames, fps)
    return tuple(replace(case.track[sample.original_frame_index]) for sample in samples)
