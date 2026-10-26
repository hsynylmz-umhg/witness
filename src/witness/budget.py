"""Pure SAM cost estimates and explicit paid-operation permission checks."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from witness.config import Settings
from witness.errors import WitnessError


@dataclass(frozen=True)
class CostEstimate:
    images: int
    input_frames: int
    billed_frames: int
    image_usd: Decimal
    video_usd: Decimal

    @property
    def total_usd(self) -> Decimal:
        return self.image_usd + self.video_usd


def estimate_cost(images: int, frames: int, settings: Settings) -> CostEstimate:
    """Frames describe one video request; a positive request has a 50-frame floor."""
    if any(type(value) is not int or value < 0 for value in (images, frames)):
        raise WitnessError("Image and frame counts must be nonnegative integers.")
    billed = max(frames, settings.sam.min_video_frames_per_request) if frames else 0
    return CostEstimate(
        images,
        frames,
        billed,
        Decimal(images) * settings.sam.image_usd_per_1000 / 1000,
        Decimal(billed) * settings.sam.video_frame_usd_per_1000 / 1000,
    )


def approved_budget(env_amount: str | None, allow_paid: bool, settings: Settings) -> Decimal:
    """Require operator opt-in, a configured cap and explicitly confirmed credits."""
    if env_amount is None:
        raise WitnessError("PENDING: WITNESS_MAX_SPEND_USD is not set; no API request sent.")
    try:
        amount = Decimal(env_amount)
    except InvalidOperation as error:
        raise WitnessError(
            "PENDING: WITNESS_MAX_SPEND_USD is invalid; no API request sent."
        ) from error
    if not amount.is_finite() or amount <= 0:
        raise WitnessError("PENDING: WITNESS_MAX_SPEND_USD must be positive; no API request sent.")
    if not allow_paid:
        raise WitnessError("PENDING: --allow-paid is required; no API request sent.")
    if settings.budget.max_usd <= 0:
        raise WitnessError("PENDING: configured budget.max_usd is zero; no API request sent.")
    if not settings.budget.credits_confirmed:
        raise WitnessError("PENDING: available credits are not confirmed; no API request sent.")
    return min(amount, settings.budget.max_usd)


def require_remaining_budget(estimate: Decimal, remaining: Decimal) -> None:
    if estimate >= remaining:
        raise WitnessError("PENDING: estimate must be below remaining budget; no API request sent.")
