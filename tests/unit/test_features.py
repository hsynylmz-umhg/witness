"""SYNTHETIC geometry and conservative continuity checks."""

import numpy as np
import pytest

from witness.errors import WitnessError
from witness.perception.features import axis_delta_deg, mask_features
from witness.perception.quality import assess_axis_pair


@pytest.fixture
def mask():
    raster = np.zeros((40, 40), dtype=np.uint8)
    raster[18:22, 8:32] = 1
    return raster


def pair(previous, current, **overrides):
    arguments = dict(
        previous_time_s=0,
        current_time_s=0.2,
        max_gap_s=0.25,
        identity_continuity_confirmed=True,
        visibility="visible",
    )
    arguments.update(overrides)
    return assess_axis_pair(previous, current, **arguments)


def test_centroid_area_and_pca_are_in_raster_coordinates(mask):
    features = mask_features(mask)
    assert features.area_px == 96
    assert features.centroid_xy == (19.5, 19.5)
    assert features.axis_deg_mod180 == pytest.approx(0)
    assert features.elongation > 2.5
    assert features.shape_valid


def test_180_degree_axis_ambiguity_does_not_create_motion(mask):
    original = mask_features(mask)
    flipped = mask_features(np.rot90(mask, 2))
    assert pair(original, flipped).delta_axis_deg == pytest.approx(0)
    assert axis_delta_deg(1, 181) == pytest.approx(0)
    assert axis_delta_deg(179, 1) == pytest.approx(2)
    assert axis_delta_deg(1, 179) == pytest.approx(-2)


def test_90_degree_direction_tie_stays_unresolved(mask):
    result = pair(mask_features(mask), mask_features(np.rot90(mask)))
    assert not result.usable_for_axis_change
    assert result.delta_axis_deg is None
    assert "axis_direction_ambiguous" in result.quality_flags


@pytest.mark.parametrize("missing", [None, np.zeros((40, 40), dtype=np.uint8)])
def test_missing_or_empty_mask_cannot_supply_axis_change(mask, missing):
    result = pair(mask_features(mask), mask_features(missing))
    assert not result.usable_for_axis_change
    assert result.delta_axis_deg is None


def test_occlusion_and_area_loss_prevent_continuity(mask):
    features = mask_features(mask)
    explicit = pair(features, features, visibility="occluded")
    heuristic = pair(features, features, reference_area_px=500)
    assert explicit.delta_axis_deg is None
    assert "occluded" in explicit.quality_flags
    assert not heuristic.usable_for_axis_change
    assert "possible_occlusion" in heuristic.quality_flags


def test_frame_exit_and_reentry_require_new_identity_confirmation(mask):
    features = mask_features(mask)
    exit_result = pair(features, features, visibility="out_of_frame")
    reentry_result = pair(features, features, identity_continuity_confirmed=False)
    assert not exit_result.usable_for_axis_change
    assert "identity_unresolved" in reentry_result.quality_flags
    assert reentry_result.delta_axis_deg is None


@pytest.mark.parametrize("time", [0, -0.1, 0.8])
def test_timestamp_discontinuity_never_gets_interpolated(mask, time):
    features = mask_features(mask)
    if time < 0:
        with pytest.raises(WitnessError):
            pair(features, features, current_time_s=time)
    else:
        result = pair(features, features, current_time_s=time)
        assert not result.usable_for_axis_change
        assert result.delta_axis_deg is None


def test_unknown_visibility_or_timestamp_quality_remains_unusable(mask):
    features = mask_features(mask)
    result = assess_axis_pair(
        features,
        features,
        previous_time_s=0,
        current_time_s=0.2,
        max_gap_s=0.25,
    )
    assert set(result.quality_flags) == {"identity_unresolved", "visibility_unknown"}
    fallback = pair(features, features, timestamp_quality_flags=("missing_original_pts",))
    assert not fallback.usable_for_axis_change


def test_square_or_boundary_mask_does_not_pass_shape_gate(mask):
    square = np.zeros_like(mask)
    square[8:32, 8:32] = 1
    assert mask_features(square).axis_deg_mod180 is None
    mask[:, :10] = 1
    result = mask_features(mask)
    assert not result.shape_valid
    assert "frame_boundary_contact" in result.quality_flags


@pytest.mark.parametrize("invalid", [np.ones((2, 2, 2)), [[0, 2]], [[float("nan")]]])
def test_malformed_masks_are_rejected(invalid):
    with pytest.raises(WitnessError):
        mask_features(np.asarray(invalid))
