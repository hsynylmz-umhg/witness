"""The zero-model-call vertical slice from SYNTHETIC masks to a hash-linked report."""

import hashlib
import json

from witness.audit.models import AuditEvent
from witness.cli import main
from witness.config import load_settings
from witness.perception.events import detect_events
from witness.synthetic.gen_masks import make_sequence, sampled_track


def test_synthetic_motion_to_audit_html_and_manifest_hash_chain(tmp_path, capsys):
    settings = load_settings()
    sequence = make_sequence(60, True, settings, name="SYNTHETIC_pipeline")
    motion = next(
        event
        for event in detect_events(sampled_track(sequence, 5), settings.detection)
        if event.status == "witnessed"
    )
    session = tmp_path / "session"
    session.mkdir()
    (session / "session.json").write_text(
        json.dumps(
            {
                "source_sha256": "SYNTHETIC_SOURCE_HASH",
                "created_at_utc": "2026-10-26T00:00:00Z",
                "video": {"decoded_frame_count": len(sequence.track)},
            }
        ),
        encoding="utf-8",
    )
    (session / "config.json").write_text(
        json.dumps({"media": {"candidate_sample_fps": 5.0}}), encoding="utf-8"
    )
    events = [
        AuditEvent("motion-1", "M4_P01", 1, motion.status, timestamp_s=motion.end_s),
        AuditEvent("manual-2", "M4_P99", 2, "corroborated"),
    ]
    (session / "events.json").write_text(
        json.dumps({"events": [event.__dict__ for event in events]}), encoding="utf-8"
    )
    output = tmp_path / "report"
    assert (
        main(
            [
                "build",
                "--session",
                str(session),
                "--procedure",
                "data/procedures/mock_panel_v1.json",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    report = (output / "report.html").read_text(encoding="utf-8")
    manifest_bytes = (output / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert "high" in report
    assert "medium" in report
    assert (output / "evidence").is_dir()
    assert (output / "findings.json").is_file()
    assert (output / "manifest.sha256").read_text(encoding="ascii").split()[0] == hashlib.sha256(
        manifest_bytes
    ).hexdigest()
    assert (
        manifest["report_hash"]
        == hashlib.sha256(
            manifest["record_hash"].encode("ascii") + (output / "report.html").read_bytes()
        ).hexdigest()
    )
    assert result["model_integration_status"] == "NOT_RUN"
