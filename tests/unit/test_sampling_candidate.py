"""Sampling-candidate tests over a fixed SYNTHETIC ten-second timeline."""

from witness.media.probe import FrameTime
from witness.media.sampling import map_sample_indices, plan_samples


def test_five_fps_selects_fifty_references_and_preserves_unknown_time_as_null():
    frames = tuple(FrameTime(index, index, index, index / 50, "pts", ()) for index in range(500))
    samples = plan_samples(frames, 5)
    assert len(samples) == 50
    assert samples[0].requested_time_s == 0.0
    assert samples[-1].requested_time_s == 9.8
    unknown = FrameTime(500, None, None, None, "missing", ("missing_timestamp",))
    mapped = map_sample_indices(frames + (unknown,), (500,))
    assert mapped[0].media_time_s is None
    assert mapped[0].pts is None
