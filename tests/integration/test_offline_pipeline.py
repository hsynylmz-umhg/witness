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


def _bare_session(tmp_path):
    session = tmp_path / "session"
    session.mkdir()
    (session / "session.json").write_text(
        json.dumps(
            {"source_sha256": "SYNTHETIC_SOURCE_HASH", "created_at_utc": "2026-10-28T00:00:00Z"}
        ),
        encoding="utf-8",
    )
    (session / "config.json").write_text("{}", encoding="utf-8")
    return session


def _build(session, output):
    return main(
        [
            "build", "--session", str(session),
            "--procedure", "data/procedures/panel_boxes_v1.json", "--out", str(output),
        ]
    )  # fmt: skip


def test_SYNTHETIC_absent_event_log_is_refused_and_writes_no_report(tmp_path, capsys):
    session, output = _bare_session(tmp_path), tmp_path / "report"
    assert _build(session, output) == 2
    message = json.loads(capsys.readouterr().err)["error"]
    assert "events.json" in message and str(session.resolve()) in message
    assert not output.exists()


def test_SYNTHETIC_empty_event_log_is_a_recorded_state_and_builds(tmp_path, capsys):
    # Present but empty: every step lacks evidence, so coverage asks for human review of each.
    session, output = _bare_session(tmp_path), tmp_path / "report"
    (session / "events.json").write_text('{"events": []}', encoding="utf-8")
    assert _build(session, output) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == 10
    findings = json.loads((output / "findings.json").read_text(encoding="utf-8"))
    rows = findings["findings"] if isinstance(findings, dict) else findings
    assert {row["kind"] for row in rows} == {"skipped"}
    assert (output / "report.html").is_file()


def test_SYNTHETIC_hand_supplied_log_reports_not_run(tmp_path, capsys):
    session, output = _bare_session(tmp_path), tmp_path / "report"
    (session / "events.json").write_text('{"events": []}', encoding="utf-8")
    assert _build(session, output) == 0
    assert json.loads(capsys.readouterr().out)["model_integration_status"] == "NOT_RUN"
    assert "&quot;model_integration_status&quot;: &quot;NOT_RUN&quot;" in (
        output / "report.html"
    ).read_text(encoding="utf-8")


def _model_session(tmp_path, anchors=3):
    session = _bare_session(tmp_path)
    events = [
        {"event_id": f"event-{n}", "part_id": f"BOX_{n:02d}", "observed_order": n,
         "status": "witnessed"}
        for n in range(1, 11)
    ]  # fmt: skip
    (session / "events.json").write_text(
        json.dumps({"producer": "model_anchor_rule_v1", "events": events}), encoding="utf-8"
    )
    (session / "model_marks.json").write_text(
        json.dumps({"model": "sam-3.1", "calls": anchors, "anchors": [{}] * anchors}),
        encoding="utf-8",
    )
    spend = session / "model" / f"spend-{session.name}"
    spend.mkdir(parents=True)
    rows = [{"status": "completed", "model": "sam-3.1", "actual_usd": "0.0025"}] * anchors
    (spend / "spend.json").write_text(json.dumps({"requests": rows}), encoding="utf-8")
    return session


def test_SYNTHETIC_model_produced_log_reports_run_with_model_anchors_and_cost(tmp_path, capsys):
    session, output = _model_session(tmp_path), tmp_path / "report"
    assert _build(session, output) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["model_integration_status"] == "RUN" and result["findings"] == 0
    assert (result["model"], result["model_anchors"], result["model_cost_usd"]) == (
        "sam-3.1", 3, "0.0075",
    )  # fmt: skip
    report = (output / "report.html").read_text(encoding="utf-8")
    assert "&quot;model_integration_status&quot;: &quot;RUN&quot;" in report
    assert "&quot;model_cost_usd&quot;: &quot;0.0075&quot;" in report


def test_SYNTHETIC_model_claim_without_its_spend_record_is_refused(tmp_path, capsys):
    session, output = _model_session(tmp_path), tmp_path / "report"
    (session / "model" / f"spend-{session.name}" / "spend.json").unlink()
    assert _build(session, output) == 2
    assert "spend record" in json.loads(capsys.readouterr().err)["error"]
    assert not output.exists()
