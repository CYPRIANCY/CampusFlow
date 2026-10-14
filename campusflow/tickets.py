from .history import append_event, validate_event_input

def calculate_priority(urgency, affected_users):
    """Calculate priority from urgency and number of affected users."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def validate_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    title = title.strip()
    if not title:
        raise ValueError("Title cannot be blank")

    return title


def normalize_title(title):
    """Normalize a title for duplicate comparisons without changing display text."""
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    normalized = " ".join(title.split()).casefold()
    if not normalized:
        raise ValueError("Title cannot be blank")
    return normalized


def validate_category(category):
    if not isinstance(category, str):
        raise ValueError("Category must be a string")

    normalized = category.strip().lower()
    allowed = ["network", "hardware", "software", "other"]

    if normalized not in allowed:
        raise ValueError(f"Category must be one of: {allowed}")

    return normalized.capitalize()


    raise ValueError(
            f"Category must be one of: {allowed}"
        )

    return normalized.capitalize()



def validate_urgency(urgency):
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be a string")

    normalized = urgency.strip().lower()

    if normalized not in ["low", "medium", "high"]:
        raise ValueError("Urgency must be low, medium, or high")

    return normalized


def validate_affected_users(value):
    if isinstance(value, bool):
        raise ValueError("Affected users must be a positive whole number")

    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        try:
            number = int(value.strip())
        except ValueError:
            raise ValueError("Affected users must be a whole number") from None
    else:
        raise ValueError("Affected users must be a whole number")

    if number <= 0:
        raise ValueError("Affected users must be positive")

    return number


def _generate_ticket_id(tickets):
    """Generate the next ticket ID from existing ticket IDs."""
    existing_numbers = []

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            existing_numbers.append(int(ticket_id[1:]))

    next_number = max(existing_numbers, default=0) + 1
    return f"T{next_number:03d}"


def create_ticket(
    tickets,
    title,
    category,
    urgency,
    affected_users,
    events=None,
    actor=None,
    now=None,
):
    """Validate input, create a ticket, and append it to the list."""
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket = {
        "id": _generate_ticket_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }

    if events is not None:
        validate_event_input(
            events,
            ticket,
            "CREATE",
            actor,
            "open",
            "open",
            "Ticket created.",
            now,
        )

    tickets.append(ticket)

    if events is not None:
        append_event(
            events=events,
            ticket=ticket,
            event_type="CREATE",
            actor=actor,
            before_status="open",
            after_status="open",
            details="Ticket created.",
            now=now,
        )

    return ticket


def detect_duplicates(tickets, category, title):
    """Return unresolved tickets matching the normalized title and category."""
    normalized_category = validate_category(category)
    normalized_title = normalize_title(title)
    return [
        ticket
        for ticket in tickets
        if ticket.get("status") != "resolved"
        and ticket.get("category") == normalized_category
        and normalize_title(ticket.get("title", "")) == normalized_title
    ]


def list_tickets(tickets):
    """Return a new list containing all tickets."""
    return list(tickets)


def get_ticket_by_id(tickets, ticket_id):
    """Find a ticket by ID, ignoring surrounding spaces and letter case."""
    if not isinstance(ticket_id, str):
        return None

    normalized_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket["id"] == normalized_id:
            return ticket


    return None

    return None

    raise ValueError(
         "Affected users must be a whole number"
        )

    raise ValueError(
            "Affected users must be a whole number"
        )

    if number <= 0:
        raise ValueError(
            "Affected users must be positive"
        )

    return number
        #value arrives as a STRING from input()
    try:
        n = int(value)
    except ValueError:
        raise ValidationError("affected_users must be a whole number")
        if n <= 0:
            raise ValidationError("affected_users must be positive")
            return n 

