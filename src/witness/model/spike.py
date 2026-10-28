"""Read box candidates out of a saved SAM image response (D032: candidate generator only).

The JSON envelope that carries the segmentation text is documented but not live-verified, so
nothing here assumes a path inside it. Every string in the response is offered to the strict
parser; only strings that parse as a complete image segmentation record count. Anything else
is ignored, and finding nothing is reported as nothing, never as zero boxes on the sheet.
"""

from collections.abc import Iterator
from typing import Any

from witness.adapters.sam_output import ParsedMask, SamParseError, parse_segmentation


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def segmentation_candidates(response: Any) -> tuple[ParsedMask, ...] | None:
    """Return the masks of the first string that parses as an image record, or None."""
    for text in _strings(response):
        try:
            records = parse_segmentation(text, media="image")
        except SamParseError:
            continue
        if records:  # a blank string parses to no records; that is not a box count
            return records
    return None
