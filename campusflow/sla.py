
from datetime import datetime, timezone, timedelta


# SLA durations are measured in minutes.
SLA_MINUTES = {
    "Critical": 60,
    "High": 240,
    "Medium": 1440,
    "Low": 2880,
}


def _require_aware_datetime(value: datetime) -> None:
    """Reject datetimes that do not contain timezone information."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must be timezone-aware.")


def calculate_due_at(priority: str, cycle_start: datetime) -> str:
    """Calculate the SLA deadline and return it as a UTC ISO-8601 string."""
    if priority not in SLA_MINUTES:
        raise ValueError(f"Invalid priority: {priority}")

    _require_aware_datetime(cycle_start)

    start_utc = cycle_start.astimezone(timezone.utc)
    due_at = start_utc + timedelta(minutes=SLA_MINUTES[priority])

    return due_at.isoformat()


def is_overdue(ticket: dict, now: datetime) -> bool:
    """Return True only when an unresolved ticket is past its SLA deadline."""
    _require_aware_datetime(now)

    if ticket.get("status") == "resolved":
        return False

    due_at_text = ticket.get("due_at")
    if not isinstance(due_at_text, str):
        raise ValueError("Ticket must have a valid due_at timestamp.")

    try:
        due_at = datetime.fromisoformat(due_at_text)
    except ValueError as exc:
        raise ValueError("Ticket due_at must be a valid ISO-8601 timestamp.") from exc

    _require_aware_datetime(due_at)

    return now.astimezone(timezone.utc) > due_at.astimezone(timezone.utc)
