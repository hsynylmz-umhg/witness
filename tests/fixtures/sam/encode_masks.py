"""Pinned reference encoder used only by synthetic conformance tests."""

import numpy as np


def encode_mask(mask: np.ndarray) -> str:
    # test-only: the pinned native package exposes its encoder only internally.
    from meta_sam_parser._mask_codec import _encode_raster

    raster = np.asarray(mask, dtype=np.uint8)
    if raster.ndim != 2 or not np.all((raster == 0) | (raster == 1)):
        raise ValueError("The test encoder requires a two-dimensional binary mask.")
    height, width = raster.shape
    return f"{height},{width}," + _encode_raster(raster.tobytes(), width, height)
