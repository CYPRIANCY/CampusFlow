import json
import os
import tempfile
import unittest

from campusflow.storage import (
    StorageError,
    load_tickets,
    save_tickets,
    load_state,
    save_state,
)

def sample_tickets():
    return [
        {
            "id": "T001",
            "title": "Campus Wi-Fi is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        },
        {
            "id": "T002",
            "title": "Laptop screen broken",
            "category": "Hardware",
            "urgency": "low",
            "affected_users": 1,
            "priority": "low",
            "status": "in_progress",
            "assigned_to": "Ada",
        },
    ]


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = os.path.join(self.temp_dir.name, "tickets.json")

    def test_save_and_reload_preserves_tickets(self):
        tickets = sample_tickets()
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_none_assigned_to_survives_round_trip(self):
        save_tickets(sample_tickets(), self.path)
        self.assertIsNone(load_tickets(self.path)[0]["assigned_to"])

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_creates_missing_folder(self):
        nested = os.path.join(self.temp_dir.name, "data", "tickets.json")
        save_tickets(sample_tickets(), nested)
        self.assertTrue(os.path.exists(nested))

    def test_malformed_json_raises_and_file_is_untouched(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "{ this is not json")

    def test_wrong_shape_raises(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"id": "T001"}, f)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_save_overwrites_previous_data(self):
        save_tickets(sample_tickets(), self.path)
        save_tickets(sample_tickets()[:1], self.path)
        self.assertEqual(len(load_tickets(self.path)), 1)

    def test_no_temp_files_left_behind(self):
        save_tickets(sample_tickets(), self.path)
        self.assertEqual(os.listdir(self.temp_dir.name), ["tickets.json"])



    def test_save_and_load_version_two_state(self):
        tickets = [
            {
                "id": "T001",
                "title": "Cannot log in",
                "status": "open",
            }
        ]

        events = [
            {
                "event_id": "E001",
                "ticket_id": "T001",
                "event_type": "CREATE",
            }
        ]

        save_state(tickets, events, self.path)
        state = load_state(self.path)

        self.assertEqual(state["schema_version"], 2)
        self.assertEqual(state["tickets"], tickets)
        self.assertEqual(state["events"], events)


    def test_saved_state_preserves_ticket_history_after_reload(self):
        tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "status": "open",
            }
        ]

        events = [
            {
                "event_id": "E0001",
                "ticket_id": "T001",
                "event_type": "CREATE",
                "actor": "operator",
                "timestamp": "2026-10-16T10:00:00+00:00",
                "before_status": "open",
                "after_status": "open",
                "details": "Ticket created.",
            }
        ]

        save_state(tickets, events, self.path)

        reloaded_state = load_state(self.path)

        self.assertEqual(reloaded_state["tickets"], tickets)
        self.assertEqual(reloaded_state["events"], events)
        self.assertEqual(
            reloaded_state["events"][0]["ticket_id"],
            reloaded_state["tickets"][0]["id"],
        )

    def test_duplicate_ticket_ids_are_rejected(self):
        tickets = [
            {"id": "T001", "title": "Wi-Fi is down"},
            {"id": "T001", "title": "Laptop is broken"},
        ]

        with self.assertRaises(StorageError):
            save_state(tickets, [], self.path)


    def test_duplicate_event_ids_are_rejected(self):
        tickets = [
            {"id": "T001", "title": "Wi-Fi is down"},
        ]

        events = [
            {"event_id": "E001", "ticket_id": "T001"},
            {"event_id": "E001", "ticket_id": "T001"},
        ]

        with self.assertRaises(StorageError):
            save_state(tickets, events, self.path)

    def test_event_referencing_unknown_ticket_is_rejected(self):
        tickets = [
            {"id": "T001", "title": "Wi-Fi is down"},
        ]

        events = [
            {
                "event_id": "E001",
                "ticket_id": "T999",
                "event_type": "CREATE",
            }
        ]

        with self.assertRaises(StorageError):
            save_state(tickets, events, self.path)


if __name__ == "__main__":
    unittest.main()
