"""SYNTHETIC SAM wire conformance, including an independent documented vector."""

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from tests.fixtures.sam.encode_masks import encode_mask
from witness.adapters import mask_codec
from witness.adapters.mask_codec import MaskDecodeError, decode_mask
from witness.adapters.sam_output import SamParseError, parse_segmentation

FIXTURES = Path(__file__).parents[1] / "fixtures/sam/conformance"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("SYNTHETIC_*.json")), ids=lambda p: p.stem)
def test_documented_rule(path):
    fixture = json.loads(path.read_text(encoding="utf-8"))
    assert fixture["data_origin"] == "SYNTHETIC"
    if "error" in fixture:
        error_type = MaskDecodeError if fixture["error"] != "sam_record" else SamParseError
        with pytest.raises(error_type) as caught:
            parse_segmentation(fixture["text"], media=fixture.get("media", "video"))
        if error_type is MaskDecodeError:
            assert caught.value.code == fixture["error"]
        return
    records = parse_segmentation(fixture["text"], media=fixture.get("media", "video"))
    assert [record.provider_object_id for record in records] == fixture["object_ids"]
    assert [record.provider_frame_index for record in records] == fixture["frames"]
    assert [list(record.raster.shape) for record in records] == fixture["shapes"]
    for record in records:
        assert record.raster.dtype == np.uint8
        assert set(np.unique(record.raster)) <= {0, 1}
    if "pixels" in fixture:
        assert records[0].raster.ravel().tolist() == fixture["pixels"]
    if "boxes" in fixture:
        assert [list(record.box_xyxy_inclusive) for record in records] == fixture["boxes"]
    if "source_sizes" in fixture:
        assert [[record.frame_width, record.frame_height] for record in records] == fixture[
            "source_sizes"
        ]


def test_two_hundred_random_binary_masks_round_trip():
    rng = np.random.default_rng(20261026)
    for _ in range(200):
        height, width = int(rng.integers(1, 33)), int(rng.integers(1, 48))
        original = rng.integers(0, 2, size=(height, width), dtype=np.uint8)
        actual = decode_mask(encode_mask(original), frame_w=64, frame_h=64)
        np.testing.assert_array_equal(actual, original)


def test_documented_vector_has_expected_pixels_without_adding_a_marker():
    actual = decode_mask("5,5,!!!!!(QO(0lu8?", 40, 40)
    expected = np.array(
        [
            [1, 0, 0, 1, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1],
            [1, 0, 0, 0, 1],
        ],
        dtype=np.uint8,
    )
    np.testing.assert_array_equal(actual, expected)


def test_payload_length_rejected_before_the_native_decoder_can_allocate(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("Native decoder called before packed-envelope validation.")

    monkeypatch.setattr(mask_codec, "decode_mask_to_raster", unexpected)
    with pytest.raises(MaskDecodeError, match="packed length"):
        decode_mask("5,5,!!!!!!(QO(0lu8?", 40, 40)
    with pytest.raises(MaskDecodeError, match="local cap"):
        decode_mask("100000,100000,!!!!!(QO(0lu8?", 100000, 100000)


def test_decoder_module_has_no_network_environment_or_file_imports():
    tree = ast.parse(Path(mask_codec.__file__).read_text(encoding="utf-8"))
    imports = {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imports |= {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not imports & {"os", "pathlib", "socket", "urllib", "requests", "http", "openai"}
