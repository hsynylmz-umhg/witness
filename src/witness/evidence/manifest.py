"""Local initial manifests and explicit integrity references."""

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from witness import __version__
from witness.errors import WitnessError
from witness.media.probe import probe_video, validate_local_video
from witness.media.sampling import plan_samples


@dataclass(frozen=True)
class IngestConfig:
    candidate_sample_fps: float = 5.0
    max_file_bytes: int = 1_073_741_824
    max_duration_seconds: float = 120.0
    max_frame_count: int = 20_000
    probe_timeout_seconds: float = 60.0

    def validate(self) -> None:
        positive_numbers = (
            self.candidate_sample_fps,
            self.max_duration_seconds,
            self.probe_timeout_seconds,
        )
        if any(
            isinstance(value, bool) or not math.isfinite(value) or value <= 0
            for value in positive_numbers
        ):
            raise WitnessError("Media rates, duration and timeout must be finite and positive.")
        if any(
            type(value) is not int or value <= 0
            for value in (self.max_file_bytes, self.max_frame_count)
        ):
            raise WitnessError("File size and frame limits must be positive integers.")


def canonical_json(value: Any) -> bytes:
    """Project canonical JSON v1: UTF-8, sorted keys, compact, no NaN or newline."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path) -> tuple[int, int, int, int]:
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def create_session(
    source: Path,
    output_root: Path,
    *,
    config: IngestConfig,
    data_origin: Literal["real", "synthetic"],
) -> Path:
    """Validate and hash input, then write a new session without modifying media."""
    config.validate()
    if data_origin not in {"real", "synthetic"}:
        raise WitnessError("Offline ingest requires an explicit real or synthetic data origin.")
    source = validate_local_video(source, max_bytes=config.max_file_bytes)
    fingerprint = _fingerprint(source)
    video = probe_video(source, timeout_s=config.probe_timeout_seconds)
    duration = max(video.declared_duration_s or 0, video.timeline_span_s)
    if duration > config.max_duration_seconds or len(video.frames) > config.max_frame_count:
        raise WitnessError("Video exceeds the configured short-clip duration or frame limit.")
    source_hash = sha256_file(source)
    if _fingerprint(source) != fingerprint:
        raise WitnessError("Input changed during inspection; no session was created.")
    samples = plan_samples(video.frames, config.candidate_sample_fps)
    if not samples:
        raise WitnessError("No timestamped frames are available for sampling.")
    session_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    effective_config = {"media": asdict(config), "sampling_status": "experimental_candidate"}
    documents: dict[str, Any] = {
        "config.json": effective_config,
        "timeline.json": {
            "schema_version": "0.1",
            "time_base": video.time_base,
            "origin_ticks": video.timeline_origin_ticks,
            "frame_index_definition": "selected_stream_decoded_presentation_order_zero_based",
            "frames": [asdict(frame) for frame in video.frames],
        },
        "samples.json": {
            "schema_version": "0.1",
            "status": "references_only_no_frames_extracted",
            "samples": [asdict(sample) for sample in samples],
        },
        "session.json": {
            "schema_version": "0.1",
            "session_id": session_id,
            "created_at_utc": created_at,
            "pipeline_version": __version__,
            "data_origin": data_origin,
            "source_filename": source.name,
            "source_sha256": source_hash,
            "source_size_bytes": fingerprint[2],
            "video": video.metadata(),
            "model_integration_status": "NOT_RUN",
            "model_versions": {},
            "observations_status": "NOT_RUN",
            "sample_count": len(samples),
        },
    }
    documents["sampling.json"] = {
        **documents["samples.json"],
        "candidate_fps": config.candidate_sample_fps,
        "unknown_time_original_frame_indices": [
            frame.original_frame_index for frame in video.frames if frame.media_time_s is None
        ],
    }
    session_dir = output_root.resolve() / session_id
    session_dir.mkdir(parents=True, exist_ok=False)
    artifacts = []
    for name, value in documents.items():
        content = canonical_json(value)
        with (session_dir / name).open("xb") as stream:
            stream.write(content)
        artifacts.append({"path": name, "sha256": hashlib.sha256(content).hexdigest()})
    manifest = {
        "schema_version": "0.1",
        "manifest_kind": "initial_offline_ingest",
        "session_id": session_id,
        "created_at_utc": created_at,
        "data_origin": data_origin,
        "pipeline_version": __version__,
        "source_sha256": source_hash,
        "config_sha256": hashlib.sha256(canonical_json(effective_config)).hexdigest(),
        "procedure_sha256": None,
        "model_versions": {},
        "parent_manifest_sha256": None,
        "artifacts": artifacts,
        "canonicalization": "witness_json_v1",
        "trust_anchor": None,
        "signature": None,
        "integrity_limitation": "Local hashes do not prevent rewriting files and their manifest.",
    }
    content = canonical_json(manifest)
    with (session_dir / "manifest.json").open("xb") as stream:
        stream.write(content)
    with (session_dir / "manifest.sha256").open("x", encoding="ascii") as stream:
        stream.write(hashlib.sha256(content).hexdigest() + "  manifest.json\n")
    return session_dir
