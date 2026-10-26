"""Strict SAM mask tuple decoding through the verified, pinned public codec API.

The body is arithmetic-coded Base85, not fixed-width bits per character. This
module performs no file, environment or network access and offers no fallback.
"""

import re

import numpy as np
from meta_sam_parser import (
    InvalidSegmentationMaskError,
    SegmentationMask,
    decode_mask_to_raster,
)
from numpy.typing import NDArray

from witness.errors import WitnessError

BASE85_ALPHABET = "".join(chr(code) for code in range(33, 124) if chr(code) not in '\\",;<>|')
BASE85_VALUES = {character: index for index, character in enumerate(BASE85_ALPHABET)}
# A local allocation ceiling, unrelated to model accuracy or provider limits.
MAX_MASK_PIXELS = 16_777_216


class MaskDecodeError(WitnessError):
    """A mask tuple violates the verified encoding or local resource contract."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def decode_mask(data: str, frame_w: int, frame_h: int) -> NDArray[np.uint8]:
    """Decode height,width,marker+payload into its own row-major binary raster.

    Validate dimensions and the exact packed-byte envelope before allocating the
    raster. The public codec validates groups, finalization and canonical one_bit
    encoding, then the decoded byte count must equal H * W. Keep the marker once.
    """
    if any(type(value) is not int or value <= 0 for value in (frame_w, frame_h)):
        raise MaskDecodeError("invalid_frame_size", "Frame dimensions must be positive integers.")
    if not isinstance(data, str):
        raise MaskDecodeError("invalid_tuple", "Mask data must be a height,width,payload string.")
    match = re.fullmatch(r"([0-9]+),([0-9]+),(.+)", data, flags=re.ASCII)
    if match is None:
        raise MaskDecodeError("invalid_tuple", "Mask data requires height, width and payload.")
    try:
        height, width = int(match[1]), int(match[2])
    except ValueError as error:
        raise MaskDecodeError("invalid_dimensions", "Mask dimensions are invalid.") from error
    area = height * width
    if height <= 0 or width <= 0 or height > frame_h or width > frame_w or area > MAX_MASK_PIXELS:
        raise MaskDecodeError(
            "invalid_dimensions", "Mask dimensions exceed the frame or local cap."
        )
    encoded = match[3]
    marker = encoded[0]
    encodings = {"!": "one_bit", "~": "lossless"}
    if marker not in encodings:
        raise MaskDecodeError("unknown_marker", "Unknown SAM mask encoding marker.")
    packed = encoded[1:]
    if len(packed) < 5:
        raise MaskDecodeError("truncated_payload", "Mask payload has no complete length prefix.")
    if any(character not in BASE85_VALUES for character in packed):
        raise MaskDecodeError("invalid_alphabet", "Mask payload contains an invalid Base85 digit.")
    byte_length = 0
    for character in packed[:5]:
        byte_length = byte_length * 85 + BASE85_VALUES[character]
    groups, tail = divmod(byte_length, 4)
    expected = 5 + groups * 5 + (tail + 1 if tail else 0)
    if len(packed) != expected:
        code = "truncated_payload" if len(packed) < expected else "malformed_length"
        raise MaskDecodeError(code, "Mask packed length does not match its prefix.")
    try:
        raster = decode_mask_to_raster(
            SegmentationMask(
                encoding=encodings[marker],
                payload=encoded,
                width=width,
                height=height,
            )
        )
    except InvalidSegmentationMaskError as error:
        raise MaskDecodeError("invalid_payload", "Mask decoding or finalization failed.") from error
    if len(raster) != area:
        raise MaskDecodeError("decoded_length", "Decoded mask length differs from height * width.")
    return np.frombuffer(raster, dtype=np.uint8).reshape(height, width).copy()
