
from datetime import datetime, timezone
from campusflow.sla import calculate_due_at

def assign_ticket(tickets, ticket_id, staff_name, events=None, actor=None, now=None):

    """Assign a ticket to a staff member. Returns the updated ticket."""
    # 1. Validate the name first
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name must not be blank.")
    cleaned_name = staff_name.strip()

    # 2. Find the ticket
    normalized_id = str(ticket_id).strip().upper()
    found = None
    for ticket in tickets:
        if ticket["id"] == normalized_id:
            found = ticket
            break

    # 3. Reject unknown and resolved tickets
    if found is None:
        raise ValueError(f"Ticket {normalized_id} not found.")
    if found["status"] == "resolved":
        raise ValueError("Resolved tickets must be reopened before changes.")

    if events is not None:
        from .history import validate_event_input

        validate_event_input(
            events,
            found,
            "ASSIGN",
            actor,
            found["status"],
            found["status"],
            f"Assigned to {cleaned_name}.",
            now,
        )

    # 4. Modify only after every check has passed
    found["assigned_to"] = cleaned_name

    if events is not None:
        from .history import append_event

        append_event(
            events,
            found,
            "ASSIGN",
            actor,
            found["status"],
            found["status"],
            f"Assigned to {cleaned_name}.",
            now,
        )
    return found


VALID_STATUSES = {"open", "in_progress", "resolved"}

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},  # explicit reopen
}


def change_status(tickets, ticket_id, new_status, now=None):
    """Change ticket status and maintain SLA timestamps and cycles."""
    # 1. Validate and normalize the new status.


def change_status(tickets, ticket_id, new_status, events=None, actor=None, now=None):
    """Move a ticket to a new status. Returns the updated ticket.

    Raises ValueError for an invalid status, unknown ticket, illegal
    transition, or moving an unassigned ticket to in_progress.
    """
    # 1. Validate and normalize the new status

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    cleaned_status = new_status.strip().lower()

    if cleaned_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'.")

    # 2. Find the ticket.
    normalized_id = str(ticket_id).strip().upper()
    found = None

    for ticket in tickets:
        if ticket["id"] == normalized_id:
            found = ticket
            break

    if found is None:
        raise ValueError(f"Ticket {normalized_id} not found.")

    # 3. Validate the requested transition.
    current_status = found["status"]

    if cleaned_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Cannot move ticket from '{current_status}' "
            f"to '{cleaned_status}'."
        )

    # 4. An unassigned ticket cannot start work.
    if cleaned_status == "in_progress" and not found["assigned_to"]:
        raise ValueError("Assign the ticket before moving it to in_progress.")


    # 5. Validate the timestamp before changing the ticket.
    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Datetime must be timezone-aware.")

    now = now.astimezone(timezone.utc)
    timestamp = now.isoformat()

    # 6. Update the ticket.
    found["status"] = cleaned_status
    found["updated_at"] = timestamp

    # 7. Reopening starts a new SLA cycle.
    if current_status == "resolved" and cleaned_status == "open":
        found["escalation_cycle"] = found.get("escalation_cycle", 0) + 1
        found["escalated_cycle"] = None
        found["due_at"] = calculate_due_at(
            found["priority"].capitalize(),
            now,
        )


    event_type = {
        "in_progress": "START",
        "resolved": "RESOLVE",
        "open": "REOPEN",
    }[cleaned_status]
    details = f"Status changed from {current_status} to {cleaned_status}."

    if events is not None:
        from .history import validate_event_input

        validate_event_input(
            events,
            found,
            event_type,
            actor,
            current_status,
            cleaned_status,
            details,
            now,
        )

    # 5. Modify only after every check has passed
    found["status"] = cleaned_status

    if events is not None:
        from .history import append_event

        append_event(
            events,
            found,
            event_type,
            actor,
            current_status,
            cleaned_status,
            details,
            now,
        )

    return found

# def change_status(tickets, ticket_id, new_status):
#     """Move a ticket to a new status. Returns the updated ticket.

#     Raises ValueError for an invalid status, unknown ticket, illegal
#     transition, or moving an unassigned ticket to in_progress.
#     """
#     # 1. Validate and normalize the new status
#     if not isinstance(new_status, str):
#         raise ValueError("Status must be text.")
#     cleaned_status = new_status.strip().lower()
#     if cleaned_status not in VALID_STATUSES:
#         raise ValueError(f"Invalid status '{new_status}'.")

#     # 2. Find the ticket
#     normalized_id = str(ticket_id).strip().upper()
#     found = None
#     for ticket in tickets:
#         if ticket["id"] == normalized_id:
#             found = ticket
#             break
#     if found is None:
#         raise ValueError(f"Ticket {normalized_id} not found.")

#     # 3. Check the transition is allowed
#     current_status = found["status"]
#     if cleaned_status not in ALLOWED_TRANSITIONS[current_status]:
#         raise ValueError(
#             f"Cannot move ticket from '{current_status}' to '{cleaned_status}'."
#         )

#     # 4. An unassigned ticket cannot start work
#     if cleaned_status == "in_progress" and not found["assigned_to"]:
#         raise ValueError("Assign the ticket before moving it to in_progress.")

#     # 5. Modify only after every check has passed
#     found["status"] = cleaned_status
#     return found
