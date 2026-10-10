    def test_valid_assignment(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_name_is_trimmed(self):
        assign_ticket(self.tickets, "t001", "  Ada  ")
        self.assertEqual(self.tickets[0]["assigned_to"], "Ada")

    def test_blank_name_rejected_and_ticket_unchanged(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_resolved_ticket_rejected(self):
        self.tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")
    
##New Code
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