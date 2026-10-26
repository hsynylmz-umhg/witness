"""Offline local input validation. This module has no API transport."""

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from witness import __version__
from witness.adapters.sam_probe import probe_image
from witness.budget import estimate_cost
from witness.config import load_settings
from witness.errors import WitnessError
from witness.evidence.manifest import IngestConfig, create_session


def load_config(path: Path | None) -> IngestConfig:
    return load_settings(path).media


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WITNESS offline video validation")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest = subparsers.add_parser(
        "ingest", help="Validate a local video and write an initial manifest"
    )
    ingest.add_argument("video", type=Path)
    ingest.add_argument("--output", type=Path, default=Path("artifacts/sessions"))
    ingest.add_argument("--config", type=Path)
    ingest.add_argument("--candidate-fps", type=float, help="Experimental sampling candidate")
    ingest.add_argument("--data-origin", choices=("real", "synthetic"), required=True)
    sam = subparsers.add_parser("sam", help="Offline estimate and explicitly gated image probe")
    sam_commands = sam.add_subparsers(dest="sam_command", required=True)
    estimate = sam_commands.add_parser(
        "estimate", help="Estimate image/one-video-request cost offline"
    )
    estimate.add_argument("--images", type=int, default=0)
    estimate.add_argument("--frames", type=int, default=0)
    estimate.add_argument("--config", type=Path)
    probe = sam_commands.add_parser(
        "probe", help="One paid image request only after all gates pass"
    )
    probe.add_argument("--image", type=Path, required=True)
    probe.add_argument("--session-dir", type=Path)
    probe.add_argument("--allow-paid", action="store_true")
    probe.add_argument("--config", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "sam":
            settings = load_settings(args.config)
            if args.sam_command == "estimate":
                cost = estimate_cost(args.images, args.frames, settings)
                print("Kind    Input  Billed  Estimated USD")
                print(f"Images  {cost.images:5d}  {cost.images:6d}  {cost.image_usd:.6f}")
                print(
                    f"Frames  {cost.input_frames:5d}  {cost.billed_frames:6d}  {cost.video_usd:.6f}"
                )
                print(f"Total estimated USD {cost.total_usd:.6f}; offline, no API request sent.")
            else:
                project_root = Path(__file__).resolve().parents[2]
                session_dir = args.session_dir or (
                    project_root / "artifacts/sam-probes" / str(uuid4())
                )
                probe_image(
                    args.image,
                    session_dir,
                    settings=settings,
                    allow_paid=args.allow_paid,
                    env_budget=os.environ.get("WITNESS_MAX_SPEND_USD"),
                    api_key=os.environ.get("MODEL_API_KEY"),
                    ledger_root=project_root / "artifacts",
                )
            return 0
        config = load_config(args.config)
        if args.candidate_fps is not None:
            config = replace(config, candidate_sample_fps=args.candidate_fps)
        session_dir = create_session(
            args.video,
            args.output,
            config=config,
            data_origin=args.data_origin,
        )
    except (WitnessError, OSError) as error:
        message = str(error) if isinstance(error, WitnessError) else "Local file operation failed."
        print(message if args.command == "sam" else json.dumps({"error": message}), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "session_id": session_dir.name,
                "manifest": str(session_dir / "manifest.json"),
                "data_origin": args.data_origin,
                "model_integration_status": "NOT_RUN",
            }
        )
    )
    return 0
