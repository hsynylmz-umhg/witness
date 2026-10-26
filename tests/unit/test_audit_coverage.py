"""Pure coverage and undocumented-observation audit checks."""

import json
from pathlib import Path

from witness.audit.coverage import coverage, undocumented
from witness.audit.models import AuditEvent, assert_findings_invariants, load_procedure


def procedure():
    path = Path("data/procedures/mock_panel_v1.json")
    return load_procedure(json.loads(path.read_text(encoding="utf-8")))


def event(part_id: str, order: int, *, status: str = "witnessed") -> AuditEvent:
    return AuditEvent(f"event-{order}", part_id, order, status, f"evidence-{order}")


def test_clean_qualified_events_produce_no_coverage_findings():
    result = coverage(
        tuple(event(step.part_id, step.order) for step in procedure().steps), procedure()
    )
    assert result == ()


def test_missing_fastener_is_high_severity_without_an_evidence_id():
    result = coverage(
        tuple(event(step.part_id, step.order) for step in procedure().steps[:-1]), procedure()
    )
    assert len(result) == 1
    assert result[0].kind == "skipped"
    assert result[0].severity == "high"
    assert result[0].part_id == "M4_P10"
    assert result[0].evidence_id is None
    assert_findings_invariants(result)


def test_empty_event_list_returns_one_review_finding_per_procedure_part():
    result = coverage((), procedure())
    assert len(result) == 10
    assert {finding.part_id for finding in result} == {f"M4_P{index:02d}" for index in range(1, 11)}


def test_undocumented_qualified_part_is_medium_severity():
    result = undocumented((event("M4_P99", 1),), procedure())
    assert len(result) == 1
    assert result[0].kind == "undocumented"
    assert result[0].severity == "medium"
    assert result[0].evidence_id == "evidence-1"
