import json
import os
import tempfile

DEFAULT_PATH = os.path.join("data", "tickets.json")


class StorageError(Exception):
    """Raised when the ticket file cannot be read safely."""


def save_tickets(tickets, path=DEFAULT_PATH):
    """Write the ticket list to a JSON file.

    Writes to a temporary file first, then swaps it in, so a crash
    while saving never leaves a half-written tickets file.
    """
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(dir=folder or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_tickets(path=DEFAULT_PATH):
    """Read tickets from a JSON file.

    Missing file -> empty list (fresh start).
    Malformed or wrongly shaped file -> StorageError (never overwritten).
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Ticket file '{path}' is not valid JSON: {error}. "
            "Fix or move the file; it was not changed."
        )

    if not isinstance(data, list) or not all(isinstance(t, dict) for t in data):
        raise StorageError(
            f"Ticket file '{path}' must contain a list of tickets."
        )
    return data
