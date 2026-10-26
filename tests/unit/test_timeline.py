"""SYNTHETIC timestamp tests, independent of any provider contract."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from witness.errors import WitnessError
from witness.media.probe import parse_probe, validate_local_video
from witness.media.sampling import map_sample_indices
from witness.media.timeline import plan_samples


@pytest.fixture
def payload():
    path = Path(__file__).parents[1] / "fixtures/synthetic/probe_vfr.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_original_pts_fallback_and_samples_have_separate_indices(payload):
    video = parse_probe(payload)
    assert video.timeline_origin_ticks == 10000
    assert [frame.media_time_s for frame in video.frames] == [0, 0.04, 0.08, 0.4]
    assert video.frames[2].pts is None
    assert video.frames[2].best_effort_timestamp == 10080
    assert video.frames[2].timestamp_source == "best_effort"
    samples = plan_samples(video.frames, 5)
    assert [sample.sample_index for sample in samples] == [0, 1]
    assert [sample.original_frame_index for sample in samples] == [0, 3]
    assert samples[1].requested_time_s == 0.2
    assert samples[1].media_time_s == 0.4
    assert "timestamp_gap_candidate" in samples[1].quality_flags


def test_missing_frame_timestamp_stays_missing(payload):
    payload["frames"][1] = {}
    video = parse_probe(payload)
    assert video.frames[1].media_time_s is None
    assert video.frames[1].pts is None
    assert "missing_timestamp" in video.frames[1].quality_flags
    assert 1 not in [sample.original_frame_index for sample in plan_samples(video.frames, 100)]
    mapped = map_sample_indices(video.frames, (1, 3))
    assert mapped[0].media_time_s is None
    assert mapped[0].pts is None
    assert mapped[1].original_frame_index == 3


@pytest.mark.parametrize("timestamp", [10000, 9999])
def test_duplicate_or_backward_pts_is_rejected(payload, timestamp):
    payload["frames"][1]["pts"] = timestamp
    with pytest.raises(WitnessError, match="increase strictly"):
        parse_probe(payload)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf")])
def test_invalid_sampling_rate_is_rejected(payload, rate):
    with pytest.raises(WitnessError):
        plan_samples(parse_probe(payload).frames, rate)


def test_sampling_above_source_rate_never_duplicates_frames(payload):
    samples = plan_samples(parse_probe(payload).frames, 100)
    assert [sample.original_frame_index for sample in samples] == [0, 1, 2, 3]
    assert "sampling_gap" in samples[-1].quality_flags


def test_no_timestamp_fps_fallback_is_invented(payload):
    payload["frames"] = [{}, {}]
    with pytest.raises(WitnessError, match="presentation timestamps"):
        parse_probe(payload)


@pytest.mark.parametrize("field,value", [("width", 0), ("time_base", "0/0")])
def test_invalid_metadata_is_rejected(payload, field, value):
    broken = deepcopy(payload)
    broken["streams"][0][field] = value
    with pytest.raises(WitnessError):
        parse_probe(broken)


def test_file_validation_rejects_directory_empty_unsupported_and_oversize(tmp_path):
    with pytest.raises(WitnessError, match="existing local file"):
        validate_local_video(tmp_path, max_bytes=4)
    path = tmp_path / "empty.mp4"
    path.touch()
    with pytest.raises(WitnessError, match="empty"):
        validate_local_video(path, max_bytes=4)
    path.write_bytes(b"12345")
    with pytest.raises(WitnessError, match="size limit"):
        validate_local_video(path, max_bytes=4)
    unknown = tmp_path / "playlist.m3u8"
    unknown.write_text("data", encoding="utf-8")
    with pytest.raises(WitnessError, match="extension"):
        validate_local_video(unknown, max_bytes=10)
