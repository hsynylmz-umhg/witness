"""Provider-independent SAM boundary, not a provider request/response schema.

Offline decoding and a documented output subset are implemented separately.
Video transport and provider frame-to-source mapping remain unverified.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol
from uuid import UUID

import numpy as np
from numpy.typing import NDArray

from witness.media.probe import FrameTime


@dataclass(frozen=True)
class SegmentationInput:
    session_id: UUID
    source_path: Path
    prompt: str
    source_frames: tuple[FrameTime, ...]
    data_origin: Literal["real", "synthetic", "cached_real"]


@dataclass(frozen=True)
class MaskObservation:
    """Normalized full-source-resolution mask after an explicitly verified mapping.

    Provider object IDs are scoped by session, prompt and response. They must not
    be treated as continuous identities after occlusion or frame exit.
    """

    session_id: UUID
    prompt: str
    provider_response_ref: str
    provider_frame_index: int
    provider_object_id: str
    original_frame_index: int | None
    source_pts: int | None
    media_time_s: float | None
    sample_index: int | None
    source_resolution_mask: NDArray[np.bool_] | None
    quality_flags: tuple[str, ...]
    data_origin: Literal["real", "synthetic", "cached_real"]


class SamAdapter(Protocol):
    """Future implementations own upload, decoding and coordinate/time mapping."""

    def segment(self, request: SegmentationInput) -> tuple[MaskObservation, ...]:
        """Return normalized observations, retaining missing or ambiguous evidence."""
        ...
