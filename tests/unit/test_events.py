"""Motion estimator checks on synthetic masks, independent of SAM access."""

from dataclasses import replace

import pytest

from tests.fixtures.synthetic.gen_masks import generate_sequences, make_sequence, sampled_track
from witness.config import load_settings
from witness.perception.events import detect_events


@pytest.fixture(scope="module")
def settings():
    return load_settings()


@pytest.mark.parametrize("rotation", [0, 15, 44, 45, 60, 94, 120])
@pytest.mark.parametrize("stop", [False, True])
def test_rotation_stop_boundary_against_ground_truth(settings, rotation, stop):
    case = make_sequence(rotation, stop, settings)
    result = detect_events(sampled_track(case, 5), settings.detection)
    witnessed = [event for event in result if event.status == "witnessed"]
    assert len(witnessed) == int(rotation >= 45 and stop)
    if rotation >= 45 and not stop:
        assert result[-1].status == "unwitnessed-tail"


@pytest.mark.parametrize(
    "condition",
    [
        "occlusion",
        "identity_switch",
        "camera_jitter",
        "timestamp_gap",
    ],
)
def test_bad_quality_never_silently_promotes_to_witnessed(settings, condition):
    case = make_sequence(94, True, settings, condition=condition)
    result = detect_events(sampled_track(case, 5), settings.detection)
    assert not any(event.status == "witnessed" for event in result)
    assert all(event.quality_flags for event in result)


def test_occlusion_after_threshold_retains_uncertain_tail(settings):
    case = make_sequence(94, True, settings, condition="occlusion")
    result = detect_events(sampled_track(case, 5), settings.detection)
    assert result[-1].status == "unwitnessed-tail"
    assert result[-1].end_s < case.track[-1].timestamp_s


def test_follow_up_session_cannot_complete_an_earlier_motion(settings):
    case = make_sequence(94, False, settings)
    track = list(sampled_track(case, 5))
    ending = track[-1]
    for index in range(1, 6):
        track.append(
            replace(
                ending,
                session_id="SYNTHETIC_follow_up",
                timestamp_s=ending.timestamp_s + index / 5,
                original_frame_index=index,
            )
        )
    events = detect_events(tuple(track), settings.detection)
    assert all(event.status != "witnessed" for event in events)
    assert events[0].session_id == case.name


def test_missing_timestamp_does_not_get_interpolated(settings):
    case = make_sequence(94, True, settings)
    track = list(sampled_track(case, 5))
    track[8] = replace(track[8], timestamp_s=None)
    result = detect_events(tuple(track), settings.detection)
    assert not any(event.status == "witnessed" for event in result)


def test_unflagged_camera_rotation_is_a_measured_estimator_limitation(settings):
    case = make_sequence(94, True, settings, condition="unflagged_camera_rotation")
    result = detect_events(sampled_track(case, 5), settings.detection)
    assert not case.ground_truth_event
    assert sum(event.status == "witnessed" for event in result) == 1


def test_results_are_deterministic_and_keep_data_origin(settings):
    case = generate_sequences(settings)[9]
    track = sampled_track(case, 5)
    first = detect_events(track, settings.detection)
    assert first == detect_events(track, settings.detection)
    assert all(event.data_origin == "synthetic" for event in first)


def test_ground_truth_does_not_change_when_detector_threshold_changes(settings):
    stricter = replace(settings, detection=replace(settings.detection, min_rotation_deg=100))
    case = make_sequence(60, True, stricter)
    assert case.ground_truth_event
    assert not any(
        event.status == "witnessed"
        for event in detect_events(
            sampled_track(case, 5),
            stricter.detection,
        )
    )
