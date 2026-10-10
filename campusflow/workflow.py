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