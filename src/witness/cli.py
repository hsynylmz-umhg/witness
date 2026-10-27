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
from witness.audit.coverage import coverage, undocumented
from witness.audit.models import (
    assert_findings_invariants,
    event_dict,
    finding_dict,
    load_audit_events,
    load_procedure,
)
from witness.audit.ordering import ordering
from witness.budget import estimate_cost
from witness.config import load_settings
from witness.errors import WitnessError
from witness.evidence.manifest import (
    IngestConfig,
    audit_record_hash,
    create_session,
    write_report_manifest,
)
from witness.perception.boxes import extract_box_events
from witness.reports.pdf import render_pdf
from witness.reports.render import EvidenceImage, render_report

_EVIDENCE_MEDIA_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
_MAX_EVIDENCE_BYTES = 20 * 1024 * 1024


def load_config(path: Path | None) -> IngestConfig:
    return load_settings(path).media


def _load_json(path: Path, description: str) -> dict[str, object] | list[object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WitnessError(f"Unable to read {description} JSON.") from error
    if not isinstance(value, (dict, list)):
        raise WitnessError(f"{description} JSON must be an object or array.")
    return value


def _copy_evidence(session_dir: Path, events, evidence_dir: Path) -> dict[str, EvidenceImage]:
    """Copy only explicit local stills from a session into a report's evidence directory."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    assets: dict[str, EvidenceImage] = {}
    session_root = session_dir.resolve()
    for event in events:
        if event.evidence_path is None:
            continue
        if event.evidence_id is None:
            raise WitnessError("An evidence path requires an evidence id.")
        relative = Path(event.evidence_path)
        if relative.is_absolute():
            raise WitnessError("Evidence paths must be relative to the session directory.")
        source = (session_root / relative).resolve()
        if not source.is_relative_to(session_root) or not source.is_file():
            raise WitnessError(
                "Evidence still must be an existing file inside the session directory."
            )
        media_type = _EVIDENCE_MEDIA_TYPES.get(source.suffix.lower())
        if media_type is None or source.stat().st_size > _MAX_EVIDENCE_BYTES:
            raise WitnessError(
                "Evidence still must be a supported image within the local size limit."
            )
        destination = evidence_dir / f"{event.evidence_id}{source.suffix.lower()}"
        content = source.read_bytes()
        destination.write_bytes(content)
        assets[event.evidence_id] = EvidenceImage(
            event.evidence_id,
            media_type,
            content,
            destination.relative_to(evidence_dir.parent).as_posix(),
        )
    return assets


def _build_report(session_dir: Path, procedure_path: Path, output_dir: Path) -> dict[str, object]:
    """Build the zero-model-call offline audit report from persisted local inputs."""
    session_dir = session_dir.resolve()
    output_dir = output_dir.resolve()
    if not session_dir.is_dir() or output_dir == session_dir:
        raise WitnessError("Report output must differ from an existing session directory.")
    session_document = _load_json(session_dir / "session.json", "session")
    config_document = _load_json(session_dir / "config.json", "session configuration")
    procedure_document = _load_json(procedure_path, "procedure")
    if not isinstance(session_document, dict) or not isinstance(config_document, dict):
        raise WitnessError("Session artifacts must be JSON objects.")
    if not isinstance(procedure_document, dict):
        raise WitnessError("Procedure JSON must be an object.")
    events_path = session_dir / "events.json"
    event_document = _load_json(events_path, "events") if events_path.exists() else {"events": []}
    procedure = load_procedure(procedure_document)
    events = load_audit_events(event_document)
    findings = (
        coverage(events, procedure) + ordering(events, procedure) + undocumented(events, procedure)
    )
    assert_findings_invariants(findings)
    report_session = {**session_document, "config": config_document}
    event_records = [event_dict(event) for event in events]
    finding_records = [finding_dict(finding) for finding in findings]
    record_hash = audit_record_hash(report_session, event_records, finding_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = _copy_evidence(session_dir, events, output_dir / "evidence")
    report_html = render_report(
        report_session, findings, record_hash=record_hash, evidence=evidence
    )
    report_path = output_dir / "report.html"
    report_path.write_bytes(report_html)
    pdf = render_pdf(report_html, output_dir / "report.pdf")
    manifest = write_report_manifest(
        output_dir,
        session=report_session,
        events=event_records,
        findings=finding_records,
        report_html=report_html,
        pdf_path=pdf.pdf_path,
        pdf_blocker_path=pdf.blocker_path,
        pdf_blocker=pdf.blocker,
    )
    return {
        "report_html": str(report_path),
        "report_pdf": str(pdf.pdf_path) if pdf.pdf_path else None,
        "pdf_blocker": str(pdf.blocker_path) if pdf.blocker_path else None,
        "manifest": str(output_dir / "manifest.json"),
        "findings": len(findings),
        "record_hash": manifest["record_hash"],
        "report_hash": manifest["report_hash"],
        "model_integration_status": "NOT_RUN",
    }


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
    build = subparsers.add_parser(
        "build", help="Build an offline audit report from an existing local session"
    )
    build.add_argument("--session", type=Path, required=True)
    build.add_argument("--procedure", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)
    boxes = subparsers.add_parser(
        "boxes", help="Write deterministic pencil-mark events for an ingested panel session"
    )
    boxes.add_argument("--session", type=Path, required=True)
    boxes.add_argument("--video", type=Path, required=True)
    boxes.add_argument("--procedure", type=Path, required=True)
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
        if args.command == "build":
            print(json.dumps(_build_report(args.session, args.procedure, args.out), sort_keys=True))
            return 0
        if args.command == "boxes":
            summary = extract_box_events(args.session, args.video, args.procedure)
            print(json.dumps(summary, sort_keys=True))
            return 0
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
