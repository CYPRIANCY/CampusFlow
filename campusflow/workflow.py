def assign_ticket(tickets, ticket_id, staff_name):
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

    # 4. Modify only after every check has passed
    found["assigned_to"] = cleaned_name
    return found


VALID_STATUSES = {"open", "in_progress", "resolved"}

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},  # explicit reopen
}


def change_status(tickets, ticket_id, new_status):
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

    # 2. Find the ticket
    normalized_id = str(ticket_id).strip().upper()
    found = None
    for ticket in tickets:
        if ticket["id"] == normalized_id:
            found = ticket
            break
    if found is None:
        raise ValueError(f"Ticket {normalized_id} not found.")

    # 3. Check the transition is allowed
    current_status = found["status"]
    if cleaned_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Cannot move ticket from '{current_status}' to '{cleaned_status}'."
        )

    # 4. An unassigned ticket cannot start work
    if cleaned_status == "in_progress" and not found["assigned_to"]:
        raise ValueError("Assign the ticket before moving it to in_progress.")

    # 5. Modify only after every check has passed
    found["status"] = cleaned_status
    return found
