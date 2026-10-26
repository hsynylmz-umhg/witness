"""Strict offline parser for the documented box/mask line subset, without transport."""

import math
import re
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from witness.adapters.mask_codec import decode_mask
from witness.errors import WitnessError


class SamParseError(WitnessError):
    """The supported, documented segmentation record subset was malformed."""


@dataclass(frozen=True)
class ParsedMask:
    provider_frame_index: int
    provider_object_id: int
    frame_width: int
    frame_height: int
    box_xyxy_inclusive: tuple[int, int, int, int]
    raster: NDArray[np.uint8]
    box_confidence: float | None
    mask_confidence: float | None


def _fields(token: str, required: set[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field in token.split(";"):
        key, separator, value = field.partition("=")
        if not separator or key in fields or key not in required | {"c"}:
            raise SamParseError("Unsupported or repeated segmentation token field.")
        fields[key] = value
    if not required <= fields.keys():
        raise SamParseError("Missing segmentation token field.")
    return fields


def _confidence(fields: dict[str, str]) -> float | None:
    if "c" not in fields:
        return None
    try:
        value = float(fields["c"])
    except ValueError as error:
        raise SamParseError("Invalid segmentation confidence.") from error
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise SamParseError("Invalid segmentation confidence.")
    return value


def parse_segmentation(text: str, *, media: str = "video") -> tuple[ParsedMask, ...]:
    """Retain sparse IDs and output order. Never infer source time or absence.

    Support the public API's explicit frame, box-then-mask, comma-delimited subset.
    Unknown extensions reject rather than being interpreted as a complete result.
    The broader native parser's forward-compatible diagnostics are not duplicated.
    """
    if media not in {"video", "image"}:
        raise SamParseError("Media kind must be image or video.")
    records: list[ParsedMask] = []
    pattern = re.compile(r"([0-9]+)<\|box;([^|]+)\|><\|mask;([^|]+)\|>", re.ASCII)
    for line in text.splitlines():
        if not line.strip():
            continue
        header = re.match(r"<([0-9]+)f>", line, re.ASCII)
        if header is None:
            raise SamParseError("Expected an explicit segmentation frame marker.")
        frame = int(header[1])
        if media == "image" and frame != 0:
            raise SamParseError("An image response must use frame zero.")
        position = header.end()
        seen_ids: set[int] = set()
        while position < len(line):
            record = pattern.match(line, position)
            if record is None:
                raise SamParseError("Malformed segmentation box/mask record.")
            identity = int(record[1])
            if identity in seen_ids:
                raise SamParseError("Repeated object ID on the same frame.")
            seen_ids.add(identity)
            box = _fields(record[2], {"x1", "y1", "x2", "y2", "w", "h"})
            mask = _fields(record[3], {"x", "y", "data"})
            if any(
                re.fullmatch(r"[0-9]+", box[key], re.ASCII) is None for key in box if key != "c"
            ):
                raise SamParseError("Box fields must use nonnegative integer source pixels.")
            x1, y1, x2, y2, width, height = (
                int(box[key]) for key in ("x1", "y1", "x2", "y2", "w", "h")
            )
            if not (0 <= x1 <= x2 < width and 0 <= y1 <= y2 < height):
                raise SamParseError("Box lies outside its repeated source dimensions.")
            if mask["x"] != "0" or mask["y"] != "0":
                raise SamParseError("Mask origin must be literal zero.")
            raster = decode_mask(mask["data"], width, height)
            records.append(
                ParsedMask(
                    frame,
                    identity,
                    width,
                    height,
                    (x1, y1, x2, y2),
                    raster,
                    _confidence(box),
                    _confidence(mask),
                )
            )
            position = record.end()
            if position < len(line):
                if line[position] != "," or position + 1 == len(line):
                    raise SamParseError("Expected a comma between segmentation records.")
                position += 1
        if not seen_ids:
            raise SamParseError("An empty frame is represented by no line, not a bare marker.")
    return tuple(records)
