"""Helpers for CampusFlow's append-only audit history."""

from datetime import datetime, timezone


VALID_EVENT_TYPES = {
    "CREATE",
    "ASSIGN",
    "START",
    "RESOLVE",
    "REOPEN",
    "ESCALATE",
}


def next_event_id(events):
    """Return the next sequential event ID without changing events."""
    numbers = []
    for event in events:
        event_id = event.get("event_id", "")
        if (
            isinstance(event_id, str)
            and event_id.startswith("E")
            and event_id[1:].isdigit()
        ):
            numbers.append(int(event_id[1:]))
    return f"E{max(numbers, default=0) + 1:04d}"


def validate_event_input(
    events,
    ticket,
    event_type,
    actor,
    before_status,
    after_status,
    details,
    now,
):
    """Validate audit data without modifying tickets or events."""
    if not isinstance(events, list):
        raise ValueError("Events must be stored in a list.")

    if not isinstance(ticket, dict) or not isinstance(ticket.get("id"), str):
        raise ValueError("An event needs a ticket with an ID.")

    if event_type not in VALID_EVENT_TYPES:
        raise ValueError("Unsupported event type.")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Actor must be a non-empty operator label.")

    if not isinstance(details, str) or not details.strip():
        raise ValueError("Details must be non-empty text.")

    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("Event time must be timezone-aware.")


def append_event(
    events,
    ticket,
    event_type,
    actor,
    before_status,
    after_status,
    details,
    now,
):
    """Create and append one successful ticket-operation event."""
    validate_event_input(
        events,
        ticket,
        event_type,
        actor,
        before_status,
        after_status,
        details,
        now,
    )

    event = {
        "event_id": next_event_id(events),
        "ticket_id": ticket["id"],
        "event_type": event_type,
        "actor": actor.strip(),
        "timestamp": now.astimezone(timezone.utc).isoformat(),
        "before_status": before_status,
        "after_status": after_status,
        "details": details.strip(),
    }

    events.append(event)
    return event


def history_for_ticket(events, ticket_id):
    """Return one ticket's events in timestamp and event-ID order."""
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text.")

    normalized_id = ticket_id.strip().upper()
    matching_events = [
        event
        for event in events
        if event["ticket_id"] == normalized_id
    ]
    return sorted(
        matching_events,
        key=lambda event: (event["timestamp"], event["event_id"]),
    )


def format_history(events, ticket_id):
    """Format one ticket's chronological audit history for CLI display."""
    normalized_id = ticket_id.strip().upper()
    history = history_for_ticket(events, ticket_id)
    if not history:
        return f"No history found for {normalized_id}."

    lines = [f"--- History for {normalized_id} ---"]
    for event in history:
        lines.append(
            "{timestamp} | {event_id} | {event_type} | {before} -> {after} | "
            "{actor}: {details}".format(
                timestamp=event["timestamp"],
                event_id=event["event_id"],
                event_type=event["event_type"],
                before=event["before_status"],
                after=event["after_status"],
                actor=event["actor"],
                details=event["details"],
            )
        )
    return "\n".join(lines)
