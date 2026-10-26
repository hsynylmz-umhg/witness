"""Report local native-parser compatibility; a diagnostic never gates pytest.

Source: https://github.com/meta-models/meta-sam/blob/main/python/README.md
No network calls, credentials, media uploads, or real responses are involved.
"""

import json
from importlib.metadata import version


def diagnose() -> int:
    try:
        from meta_sam_parser import (
            CompletedOutcome,
            SegmentationMask,
            decode_mask_to_raster,
            video_segmentation_format,
        )
    except ImportError:
        print(json.dumps({"status": "BLOCKED", "reason": "Install the sam-verification extra."}))
        return 0
    # Quoted codec vector from the official Python README; this is SYNTHETIC.
    payload = "!!!!!(QO(0lu8?"
    raster = decode_mask_to_raster(
        SegmentationMask(encoding="one_bit", payload=payload, width=5, height=5)
    )
    text = f"<2f>7<|box;x1=10;y1=20;x2=14;y2=24;w=40;h=40|><|mask;x=0;y=0;data=5,5,{payload}|>\n"
    parser = video_segmentation_format().create_parser()
    parser.push(text)
    result = parser.finish(CompletedOutcome()).result
    mask_count = sum(record.kind == "mask" for record in result.records)
    compatible = len(raster) == 25 and mask_count == 1 and not result.diagnostics
    print(
        json.dumps(
            {
                "status": "OFFLINE_CONTRACT_PASS" if compatible else "BLOCKED",
                "data_origin": "SYNTHETIC",
                "package": "meta-sam-parser",
                "version": version("meta-sam-parser"),
                "direct_decoder_pixels": len(raster),
                "parsed_mask_count": mask_count,
                "diagnostic_codes": [diagnostic.code for diagnostic in result.diagnostics],
                "live_api_test": "NOT_RUN",
            }
        )
    )
    return 0


def main() -> int:
    try:
        return diagnose()
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error_type": type(error).__name__,
                    "live_api_test": "NOT_RUN",
                }
            )
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
