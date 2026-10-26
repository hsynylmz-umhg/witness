"""Local ffmpeg/ffprobe tests using generated SYNTHETIC video, never SAM."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from uuid import UUID

import pytest

from witness.cli import main
from witness.errors import WitnessError
from witness.evidence.manifest import IngestConfig, canonical_json, create_session, sha256_file
from witness.media.probe import probe_video

pytestmark = pytest.mark.ffmpeg


@pytest.fixture
def video(tmp_path):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None or shutil.which("ffprobe") is None:
        pytest.skip("Local ffmpeg and ffprobe are required for SYNTHETIC media tests.")
    source = tmp_path / "SYNTHETIC_clip.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=96x64:rate=25",
            "-t",
            "1",
            "-c:v",
            "mpeg4",
            "-bf",
            "2",
            "-output_ts_offset",
            "2",
            str(source),
        ],
        check=True,
        capture_output=True,
        timeout=20,
    )
    return source


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_cli_produces_hash_linked_manifest_and_preserves_pts(video, tmp_path, capsys):
    original_bytes = video.read_bytes()
    assert (
        main(
            [
                "ingest",
                str(video),
                "--output",
                str(tmp_path / "sessions"),
                "--data-origin",
                "synthetic",
                "--candidate-fps",
                "5",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    manifest_path = Path(output["manifest"])
    manifest = read(manifest_path)
    session = read(manifest_path.parent / "session.json")
    timeline = read(manifest_path.parent / "timeline.json")
    samples = read(manifest_path.parent / "samples.json")["samples"]
    assert read(manifest_path.parent / "sampling.json")["samples"] == samples
    assert UUID(session["session_id"]).version == 4
    assert session["created_at_utc"].endswith("Z")
    assert session["data_origin"] == "synthetic"
    assert session["model_integration_status"] == "NOT_RUN"
    assert session["source_sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert session["video"]["decoded_frame_count"] == 25
    assert timeline["frames"][0]["pts"] > 0
    assert timeline["frames"][0]["media_time_s"] == 0
    assert [sample["original_frame_index"] for sample in samples] == [0, 5, 10, 15, 20]
    for artifact in manifest["artifacts"]:
        assert sha256_file(manifest_path.parent / artifact["path"]) == artifact["sha256"]
        assert not Path(artifact["path"]).is_absolute()
    assert (manifest_path.parent / "manifest.sha256").read_text().split()[0] == sha256_file(
        manifest_path
    )
    assert video.read_bytes() == original_bytes


def test_later_clip_is_a_new_session_and_does_not_rewrite_first(video, tmp_path):
    output = tmp_path / "sessions"
    first = create_session(video, output, config=IngestConfig(), data_origin="synthetic")
    snapshot = (first / "manifest.json").read_bytes()
    later = tmp_path / "SYNTHETIC_later.mp4"
    later.write_bytes(video.read_bytes() + b"SYNTHETIC_DIFFERENT_BYTES")
    second = create_session(later, output, config=IngestConfig(), data_origin="synthetic")
    assert first != second
    assert (
        read(first / "manifest.json")["source_sha256"]
        != read(second / "manifest.json")["source_sha256"]
    )
    assert read(second / "manifest.json")["parent_manifest_sha256"] is None
    assert (first / "manifest.json").read_bytes() == snapshot


def test_short_clip_limit_rejection_writes_no_session(video, tmp_path):
    output = tmp_path / "sessions"
    with pytest.raises(WitnessError, match="short-clip"):
        create_session(
            video, output, config=IngestConfig(max_duration_seconds=0.5), data_origin="synthetic"
        )
    assert not output.exists()


def test_corrupt_video_returns_safe_error(tmp_path, capsys):
    source = tmp_path / "private_name.mp4"
    source.write_bytes(b"SYNTHETIC_NOT_A_VIDEO")
    assert main(["ingest", str(source), "--data-origin", "synthetic"]) == 2
    result = capsys.readouterr()
    assert result.out == ""
    assert "private_name" not in result.err
    assert "ffprobe could not decode" in json.loads(result.err)["error"]


def test_canonical_json_is_deterministic_and_refuses_nonfinite_numbers():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})
    with pytest.raises(ValueError):
        canonical_json({"bad": float("nan")})


def test_real_ffprobe_retains_a_synthetic_vfr_gap(video, tmp_path):
    vfr = tmp_path / "SYNTHETIC_vfr.mp4"
    subprocess.run(
        [
            shutil.which("ffmpeg"),
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=96x64:rate=10",
            "-t",
            "1",
            "-vf",
            r"select=not(eq(n\,3))",
            "-fps_mode",
            "vfr",
            "-c:v",
            "mpeg4",
            str(vfr),
        ],
        check=True,
        capture_output=True,
        timeout=20,
    )
    info = probe_video(vfr)
    assert [frame.media_time_s for frame in info.frames[:4]] == [0, 0.1, 0.2, 0.4]
    assert "timestamp_gap_candidate" in info.frames[3].quality_flags


def test_source_change_during_inspection_creates_no_manifest(video, tmp_path, monkeypatch):
    from witness.evidence import manifest as module

    actual_hash = module.sha256_file

    def changed_hash(path):
        with path.open("ab") as stream:
            stream.write(b"SYNTHETIC_MUTATION")
        return actual_hash(path)

    monkeypatch.setattr(module, "sha256_file", changed_hash)
    output = tmp_path / "sessions"
    with pytest.raises(WitnessError, match="changed during inspection"):
        create_session(video, output, config=IngestConfig(), data_origin="synthetic")
    assert not output.exists()
