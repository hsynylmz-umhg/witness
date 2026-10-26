"""Pure coverage and undocumented-observation audit functions."""

from witness.audit.models import AuditEvent, Finding, Procedure, assert_findings_invariants


def coverage(events: tuple[AuditEvent, ...], procedure: Procedure) -> tuple[Finding, ...]:
    """Return a high-severity review finding for each procedure part without evidence."""
    observed_parts = {event.part_id for event in events if event.is_qualified}
    findings = tuple(
        Finding(
            finding_id=f"skipped:{step.step_id}",
            kind="skipped",
            severity="high",
            part_id=step.part_id,
            step_id=step.step_id,
            message=(
                "No witnessed or corroborated event is available for this procedure part; "
                "human review is required."
            ),
        )
        for step in procedure.steps
        if step.part_id not in observed_parts
    )
    assert_findings_invariants(findings)
    return findings


def undocumented(events: tuple[AuditEvent, ...], procedure: Procedure) -> tuple[Finding, ...]:
    """Return medium-severity findings for qualified parts absent from the procedure."""
    procedure_parts = {step.part_id for step in procedure.steps}
    return tuple(
        Finding(
            finding_id=f"undocumented:{event.event_id}",
            kind="undocumented",
            severity="medium",
            part_id=event.part_id,
            event_id=event.event_id,
            evidence_id=event.evidence_id,
            message="A qualified observed part is absent from the supplied procedure.",
        )
        for event in events
        if event.is_qualified and event.part_id not in procedure_parts
    )
