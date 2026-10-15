
from datetime import datetime, timezone

from campusflow.sla import is_overdue


def _next_event_id(events: list[dict]) -> str:
    """Generate an event ID that does not already exist."""
    existing_ids = {
        event.get("event_id")
        for event in events
    }

    number = 1
    while True:
        event_id = f"E{number:04d}"
        if event_id not in existing_ids:
            return event_id
        number += 1


def escalate_overdue(
    tickets: list[dict],
    events: list[dict],
    now: datetime,
    actor: str,
) -> dict:
    """Escalate overdue unresolved tickets once per SLA cycle."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Datetime must be timezone-aware.")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Actor must be a non-empty string.")

    timestamp = now.astimezone(timezone.utc).isoformat()

    newly_escalated = 0
    already_escalated = 0

    for ticket in tickets:
        # Resolved and not-yet-overdue tickets are skipped.
        if not is_overdue(ticket, now):
            continue

        current_cycle = ticket.get("escalation_cycle", 0)

        # Prevent a second escalation in the same SLA cycle.
        if ticket.get("escalated_cycle") == current_cycle:
            already_escalated += 1
            continue

        event = {
            "event_id": _next_event_id(events),
            "ticket_id": ticket["id"],
            "event_type": "ESCALATE",
            "actor": actor.strip(),
            "timestamp": timestamp,
            "before_status": ticket["status"],
            "after_status": ticket["status"],
            "details": {
                "priority": ticket["priority"],
                "escalation_cycle": current_cycle,
            },
        }

        # Record the successful escalation and mark its cycle.
        events.append(event)
        ticket["escalated_cycle"] = current_cycle
        newly_escalated += 1

    return {
        "newly_escalated": newly_escalated,
        "already_escalated": already_escalated,
    }
