"""Pure longest-increasing-subsequence ordering audit checks."""

import json
from pathlib import Path

from witness.audit.models import AuditEvent, load_procedure
from witness.audit.ordering import ordering


def procedure():
    return load_procedure(json.loads(Path("data/procedures/mock_panel_v1.json").read_text()))


def test_ordered_events_have_no_order_discrepancy():
    events = (
        AuditEvent("event-1", "M4_P01", 1, "witnessed"),
        AuditEvent("event-2", "M4_P02", 2, "corroborated"),
    )
    assert ordering(events, procedure()) == ()


def test_out_of_order_pair_reports_only_one_minimum_review_set_member():
    events = (
        AuditEvent("event-2", "M4_P02", 1, "witnessed", "evidence-2"),
        AuditEvent("event-1", "M4_P01", 2, "witnessed", "evidence-1"),
    )
    result = ordering(events, procedure())
    assert len(result) == 1
    assert result[0].kind == "order_discrepancy"
    assert result[0].severity == "high"
    assert result[0].evidence_id in {"evidence-1", "evidence-2"}


def test_undocumented_or_unqualified_events_do_not_create_order_findings():
    events = (
        AuditEvent("event-1", "M4_P99", 1, "witnessed"),
        AuditEvent("event-2", "M4_P02", 2, "inferred"),
    )
    assert ordering(events, procedure()) == ()
