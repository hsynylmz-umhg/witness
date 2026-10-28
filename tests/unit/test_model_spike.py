"""SYNTHETIC responses for the round-13 model spike reader; no network."""

import json
from pathlib import Path

from witness.adapters import sam_probe
from witness.config import load_settings
from witness.model.spike import segmentation_candidates

LINE = json.loads(
    (
        Path(__file__).parents[1] / "fixtures/sam/conformance/SYNTHETIC_inclusive_box_corners.json"
    ).read_text(encoding="utf-8")
)["text"]


def test_SYNTHETIC_candidates_are_found_wherever_the_envelope_puts_the_text():
    response = {"status": "completed", "output": [{"content": [{"text": LINE}]}]}
    (mask,) = segmentation_candidates(response)
    assert mask.box_xyxy_inclusive == (315, 329, 319, 333)


def test_SYNTHETIC_no_parsable_text_is_none_not_zero_boxes():
    assert segmentation_candidates({"status": "completed", "output": "box 1, left edge"}) is None
    assert segmentation_candidates({"status": "completed", "output": ""}) is None
    assert segmentation_candidates({"status": "completed"}) is None


def test_SYNTHETIC_sink_receives_the_raw_bytes_and_the_prompt_is_sent(monkeypatch):
    raw = b'{"status":"completed","output":[]}'
    sent = []

    class Reply:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self, _):
            return raw

    class Opener:
        def open(self, request, timeout):
            sent.append(json.loads(request.data))
            return Reply()

    monkeypatch.setattr(sam_probe, "build_opener", lambda handler: Opener())
    received = []
    result = sam_probe.send_image(
        b"SYNTHETIC", "image/jpeg", "SYNTHETIC_TOKEN", load_settings(),
        prompt="printed square box", sink=received.append,
    )  # fmt: skip
    assert result == {"completed_images": 1}
    assert received == [raw]
    assert sent[0]["input"][0]["content"][0]["text"] == "printed square box"
