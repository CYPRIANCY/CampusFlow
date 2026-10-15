
def get_ticket_queue(tickets):
    """Return open tickets ordered by priority and numeric ticket ID."""

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(
        open_tickets,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:])
        )
    )


def get_sla_attention_queue(tickets, now, overdue_checker):
    """Return unresolved tickets ordered by SLA attention urgency.

    The injected checker keeps the queue independent from the SLA calculation
    implementation while guaranteeing that it uses the same overdue rule.
    """
    if not callable(overdue_checker):
        raise ValueError("An overdue checker is required.")

    unresolved = [
        ticket
        for ticket in tickets
        if ticket.get("status") in {"open", "in_progress"}
    ]
    return sorted(
        unresolved,
        key=lambda ticket: (
            0 if overdue_checker(ticket, now) else 1,
            ticket["due_at"],
            int(ticket["id"][1:]),
        ),
    )
