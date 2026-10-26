"""Explicit project settings; loading occurs only when called."""

import math
import tomllib
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from witness.errors import WitnessError
from witness.evidence.manifest import IngestConfig


@dataclass(frozen=True)
class DetectorConfig:
    min_rotation_deg: float
    movement_delta_deg: float
    stop_delta_deg: float
    stop_centroid_px: float
    min_stop_samples: int
    min_stop_seconds: float
    max_gap_seconds: float
    max_axis_step_deg: float
    max_event_seconds: float
    min_pixels: int
    min_elongation: float
    min_area_ratio: float
    area_history_samples: int
    numeric_tolerance_deg: float


@dataclass(frozen=True)
class BudgetConfig:
    max_usd: Decimal
    credits_confirmed: bool


@dataclass(frozen=True)
class SamConfig:
    image_usd_per_1000: Decimal
    video_frame_usd_per_1000: Decimal
    min_video_frames_per_request: int
    timeout_seconds: float
    max_image_bytes: int
    max_response_bytes: int


@dataclass(frozen=True)
class Settings:
    media: IngestConfig
    detection: DetectorConfig
    budget: BudgetConfig
    sam: SamConfig


def _decimal(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except InvalidOperation as error:
        raise WitnessError("Invalid decimal configuration value.") from error
    if not amount.is_finite() or amount < 0:
        raise WitnessError("Configuration money values must be finite and nonnegative.")
    return amount


def load_settings(path: Path | None = None) -> Settings:
    """Merge explicit table overrides with the single checked-in defaults file."""
    default_path = Path(__file__).resolve().parents[2] / "config/defaults.toml"
    try:
        with default_path.open("rb") as stream:
            tables = tomllib.load(stream)
        if path is not None and path.resolve() != default_path:
            with path.open("rb") as stream:
                override = tomllib.load(stream)
            if not override.keys() <= tables.keys():
                raise WitnessError("Unknown configuration table.")
            for name, values in override.items():
                if not isinstance(values, dict) or not values.keys() <= tables[name].keys():
                    raise WitnessError("Unknown configuration field.")
                tables[name].update(values)
        media = IngestConfig(**tables["media"])
        media.validate()
        detection = DetectorConfig(**tables["detection"])
        validate_detector_config(detection)
        budget_values = tables["budget"]
        if type(budget_values["credits_confirmed"]) is not bool:
            raise WitnessError("Credit confirmation must be boolean.")
        budget = BudgetConfig(
            _decimal(budget_values["max_usd"]), budget_values["credits_confirmed"]
        )
        sam_values = dict(tables["sam"])
        for name in ("image_usd_per_1000", "video_frame_usd_per_1000"):
            sam_values[name] = _decimal(sam_values[name])
        sam = SamConfig(**sam_values)
        for value in (
            sam.min_video_frames_per_request,
            sam.max_image_bytes,
            sam.max_response_bytes,
        ):
            if type(value) is not int or value <= 0:
                raise WitnessError("SAM local limits must be positive integers.")
        if not math.isfinite(sam.timeout_seconds) or sam.timeout_seconds <= 0:
            raise WitnessError("SAM timeout must be finite and positive.")
        if sam.image_usd_per_1000 <= 0 or sam.video_frame_usd_per_1000 <= 0:
            raise WitnessError("Verified SAM unit prices must be positive.")
        return Settings(media, detection, budget, sam)
    except (OSError, TypeError, KeyError, tomllib.TOMLDecodeError) as error:
        raise WitnessError("Unable to load the project configuration.") from error


def validate_detector_config(config: DetectorConfig) -> None:
    import math
    from dataclasses import fields

    for field in fields(config):
        value = getattr(config, field.name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (float, int))
            or not math.isfinite(value)
        ):
            raise WitnessError("Detector thresholds must be finite numbers.")
        if value < 0:
            raise WitnessError("Detector thresholds must be nonnegative.")
    for value in (config.min_stop_samples, config.min_pixels, config.area_history_samples):
        if type(value) is not int or value < 1:
            raise WitnessError("Detector sample counts must be positive integers.")
    if not (
        config.min_rotation_deg > 0
        and config.max_gap_seconds > 0
        and config.max_event_seconds > 0
        and 0 < config.max_axis_step_deg < 90
        and config.min_elongation > 1
        and 0 < config.min_area_ratio <= 1
        and config.min_pixels >= 2
        and config.movement_delta_deg > config.stop_delta_deg
    ):
        raise WitnessError("Detector threshold relationships are invalid.")
