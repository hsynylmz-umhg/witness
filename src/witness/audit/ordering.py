"""Pure minimum-review-set ordering audit based on a longest increasing subsequence."""

from witness.audit.models import AuditEvent, Finding, Procedure


def _longest_increasing_indices(values: tuple[int, ...]) -> tuple[int, ...]:
    """Return one deterministic LIS using earliest-index tie breaking."""
    lengths = [1] * len(values)
    predecessors: list[int | None] = [None] * len(values)
    for current, value in enumerate(values):
        for previous in range(current):
            if values[previous] < value and lengths[previous] + 1 > lengths[current]:
                lengths[current] = lengths[previous] + 1
                predecessors[current] = previous
    if not values:
        return ()
    endpoint = max(range(len(values)), key=lambda index: (lengths[index], -index))
    indices = []
    while endpoint is not None:
        indices.append(endpoint)
        endpoint = predecessors[endpoint]
    return tuple(reversed(indices))


def ordering(events: tuple[AuditEvent, ...], procedure: Procedure) -> tuple[Finding, ...]:
    """Report only one minimum set requiring order review, never a physical conclusion."""
    order_by_part = {step.part_id: step.order for step in procedure.steps}
    relevant = tuple(
        event for event in events if event.is_qualified and event.part_id in order_by_part
    )
    retained = set(
        _longest_increasing_indices(tuple(order_by_part[event.part_id] for event in relevant))
    )
    return tuple(
        Finding(
            finding_id=f"order:{event.event_id}",
            kind="order_discrepancy",
            severity="high",
            part_id=event.part_id,
            event_id=event.event_id,
            evidence_id=event.evidence_id,
            message=(
                "This event is in one minimum order-review set outside a longest increasing "
                "subsequence; it is not a conclusion about physical assembly correctness."
            ),
        )
        for index, event in enumerate(relevant)
        if index not in retained
    )
