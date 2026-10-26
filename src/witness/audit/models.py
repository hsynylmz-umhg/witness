"""Provider-independent procedure, observation, and audit finding contracts."""

from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping

from witness.errors import WitnessError

QualifiedStatus = Literal["witnessed", "corroborated"]


@dataclass(frozen=True)
class ProcedureStep:
    """One ordered, uniquely identified mock-panel procedure step."""

    step_id: str
    order: int
    action: str
    part_id: str
    tool: str
    verbatim: str


@dataclass(frozen=True)
class Procedure:
    """A hand-authored or future-provider procedure contract."""

    procedure_id: str
    rev: str
    steps: tuple[ProcedureStep, ...]


@dataclass(frozen=True)
class AuditEvent:
    """An event associated with a part before deterministic audit evaluation."""

    event_id: str
    part_id: str
    observed_order: int
    status: str
    evidence_id: str | None = None
    evidence_path: str | None = None
    timestamp_s: float | None = None

    @property
    def is_qualified(self) -> bool:
        """Only qualified visual states participate in deterministic audit claims."""
        return self.status in {"witnessed", "corroborated"}


@dataclass(frozen=True)
class Finding:
    """A deterministic review finding; never a physical assembly conclusion."""

    finding_id: str
    kind: Literal["skipped", "order_discrepancy", "undocumented"]
    severity: Literal["high", "medium"]
    part_id: str
    message: str
    step_id: str | None = None
    event_id: str | None = None
    evidence_id: str | None = None


def assert_findings_invariants(findings: tuple[Finding, ...]) -> None:
    """Enforce the evidence boundary before a report is rendered or persisted."""
    assert all(finding.evidence_id is None for finding in findings if finding.kind == "skipped"), (
        "A skipped finding must not carry an evidence id."
    )


def finding_dict(finding: Finding) -> dict[str, Any]:
    """Return stable JSON-compatible output for a finding."""
    return asdict(finding)


def event_dict(event: AuditEvent) -> dict[str, Any]:
    """Return stable JSON-compatible output for an audit event."""
    return asdict(event)


def load_procedure(data: Mapping[str, Any]) -> Procedure:
    """Validate the future procedure response shape at the I/O boundary."""
    required = {"procedure_id", "rev", "steps"}
    if not required <= data.keys() or not isinstance(data["steps"], list):
        raise WitnessError("Procedure must contain procedure_id, rev, and a steps array.")
    if not all(isinstance(data[key], str) and data[key] for key in ("procedure_id", "rev")):
        raise WitnessError("Procedure identifiers must be nonempty strings.")
    steps: list[ProcedureStep] = []
    expected_step_keys = {"step_id", "order", "action", "part_id", "tool", "verbatim"}
    for value in data["steps"]:
        if not isinstance(value, Mapping) or set(value) != expected_step_keys:
            raise WitnessError("Every procedure step must match the documented procedure schema.")
        if (
            not isinstance(value["order"], int)
            or isinstance(value["order"], bool)
            or value["order"] <= 0
            or not all(
                isinstance(value[key], str) and value[key] for key in expected_step_keys - {"order"}
            )
        ):
            raise WitnessError("Procedure steps require positive order and nonempty text fields.")
        steps.append(ProcedureStep(**value))
    if not steps or len({step.step_id for step in steps}) != len(steps):
        raise WitnessError("Procedure steps must be nonempty and use unique step_id values.")
    if len({step.order for step in steps}) != len(steps) or len(
        {step.part_id for step in steps}
    ) != len(steps):
        raise WitnessError("This offline audit slice requires unique step orders and part ids.")
    return Procedure(
        str(data["procedure_id"]),
        str(data["rev"]),
        tuple(sorted(steps, key=lambda step: step.order)),
    )


def load_audit_events(data: Any) -> tuple[AuditEvent, ...]:
    """Validate the local events artifact without interpreting a provider response."""
    values = data.get("events") if isinstance(data, Mapping) else data
    if not isinstance(values, list):
        raise WitnessError("Events artifact must be an array or an object with an events array.")
    events: list[AuditEvent] = []
    required = {"event_id", "part_id", "observed_order", "status"}
    optional = {"evidence_id", "evidence_path", "timestamp_s"}
    for value in values:
        if (
            not isinstance(value, Mapping)
            or not required <= value.keys()
            or not set(value) <= required | optional
        ):
            raise WitnessError("Each audit event must match the documented local event schema.")
        if not all(
            isinstance(value[key], str) and value[key] for key in ("event_id", "part_id", "status")
        ):
            raise WitnessError("Audit event text fields must be nonempty strings.")
        if (
            not isinstance(value["observed_order"], int)
            or isinstance(value["observed_order"], bool)
            or value["observed_order"] <= 0
        ):
            raise WitnessError("Audit event observed_order must be a positive integer.")
        for key in ("evidence_id", "evidence_path"):
            if key in value and value[key] is not None and not isinstance(value[key], str):
                raise WitnessError("Audit evidence references must be strings or null.")
        if value.get("timestamp_s") is not None and not isinstance(
            value["timestamp_s"], (int, float)
        ):
            raise WitnessError("Audit event timestamp_s must be a number or null.")
        events.append(
            AuditEvent(
                event_id=value["event_id"],
                part_id=value["part_id"],
                observed_order=value["observed_order"],
                status=value["status"],
                evidence_id=value.get("evidence_id"),
                evidence_path=value.get("evidence_path"),
                timestamp_s=value.get("timestamp_s"),
            )
        )
    if len({event.event_id for event in events}) != len(events):
        raise WitnessError("Audit event ids must be unique.")
    if len({event.observed_order for event in events}) != len(events):
        raise WitnessError("Audit event observed_order values must be unique.")
    return tuple(sorted(events, key=lambda event: event.observed_order))
