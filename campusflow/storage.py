
import json
import os
import tempfile

DEFAULT_PATH = os.path.join("data", "tickets.json")
SCHEMA_VERSION = 2


class StorageError(Exception):
    """Raised when stored data cannot be read or validated safely."""


def _validate_state(data, path):
    """Check that data follows the version-2 storage format."""
    if not isinstance(data, dict):
        raise StorageError(
            f"Ticket file '{path}' must contain a version-2 JSON object."
        )

    if data.get("schema_version") != SCHEMA_VERSION:
        raise StorageError(
            f"Ticket file '{path}' has an unsupported schema version. "
            "Expected version 2. The file was not changed."
        )

    tickets = data.get("tickets")
    events = data.get("events")

    if not isinstance(tickets, list) or not all(
        isinstance(ticket, dict) for ticket in tickets
    ):
        raise StorageError(
            f"Ticket file '{path}' must contain a list of ticket objects."
        )

    ticket_ids = []

    for ticket in tickets:
        ticket_id = ticket.get("id")

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise StorageError(
                f"Ticket file '{path}' contains a ticket "
                "with a missing or invalid ID."
            )

        if ticket_id in ticket_ids:
            raise StorageError(
                f"Ticket file '{path}' contains duplicate ticket ID "
                f"'{ticket_id}'."
            )

        ticket_ids.append(ticket_id)

    if not isinstance(events, list) or not all(
        isinstance(event, dict) for event in events
    ):
        raise StorageError(
            f"Ticket file '{path}' must contain a list of event objects."
        )


def _write_state(data, path):
    """Write JSON atomically so incomplete writes do not replace the file."""
    folder = os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        dir=folder or ".",
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        os.replace(temp_path, path)

    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def save_state(tickets, events, path=DEFAULT_PATH):
    """Save tickets and history events in version-2 format."""
    data = {
        "schema_version": SCHEMA_VERSION,
        "tickets": tickets,
        "events": events,
    }

    _validate_state(data, path)
    _write_state(data, path)


def load_state(path=DEFAULT_PATH):
    """Load and validate version-2 state without modifying the file."""
    if not os.path.exists(path):
        return {
            "schema_version": SCHEMA_VERSION,
            "tickets": [],
            "events": [],
        }

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise StorageError(
            f"Ticket file '{path}' is not valid JSON: {error}. "
            "Fix or move the file; it was not changed."
        ) from error

    except OSError as error:
        raise StorageError(
            f"Could not read ticket file '{path}': {error}"
        ) from error

    _validate_state(data, path)
    return data


def save_tickets(tickets, path=DEFAULT_PATH):
    """Save tickets while preserving existing history events."""
    events = []

    if os.path.exists(path):
        state = load_state(path)
        events = state["events"]

    save_state(tickets, events, path)


def load_tickets(path=DEFAULT_PATH):
    """Load tickets using the existing interface used by main.py."""
    return load_state(path)["tickets"]
