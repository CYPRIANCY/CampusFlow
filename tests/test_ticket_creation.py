
import unittest
from datetime import datetime, timezone

from campusflow.tickets import (
    create_ticket,
    detect_duplicates,
    list_tickets,
    get_ticket_by_id,
)


class TestTicketCreation(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_first_ticket_gets_t001(self):
        ticket = create_ticket(
            self.tickets, "Wi-Fi is down", "Network", "high", "12"
        )
        self.assertEqual(ticket["id"], "T001")

    def test_second_ticket_gets_t002(self):
        create_ticket(
            self.tickets, "Wi-Fi is down", "Network", "high", "12"
        )
        ticket = create_ticket(
            self.tickets, "Laptop broken", "Hardware", "low", "1"
        )
        self.assertEqual(ticket["id"], "T002")

    def test_ticket_has_expected_default_values(self):
        ticket = create_ticket(
            self.tickets, "App is crashing", "Software", "medium", "3"
        )
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["priority"], "medium")

    def test_creation_adds_ticket_to_collection(self):
        create_ticket(
            self.tickets, "Printer problem", "Hardware", "low", "1"
        )
        self.assertEqual(len(self.tickets), 1)

    def test_list_tickets_returns_all_tickets(self):
        create_ticket(
            self.tickets, "Wi-Fi is down", "Network", "high", "12"
        )
        create_ticket(
            self.tickets, "Laptop broken", "Hardware", "low", "1"
        )
        result = list_tickets(self.tickets)
        self.assertEqual(len(result), 2)

    def test_list_tickets_does_not_return_original_list(self):
        result = list_tickets(self.tickets)
        self.assertIsNot(result, self.tickets)

    def test_get_ticket_by_id_finds_ticket(self):
        created = create_ticket(
            self.tickets, "Wi-Fi is down", "Network", "high", "12"
        )
        result = get_ticket_by_id(self.tickets, "T001")
        self.assertEqual(result, created)

    def test_ticket_lookup_is_case_insensitive(self):
        create_ticket(
            self.tickets, "Wi-Fi is down", "Network", "high", "12"
        )
        self.assertIsNotNone(get_ticket_by_id(self.tickets, "t001"))

    def test_unknown_ticket_id_returns_none(self):
        result = get_ticket_by_id(self.tickets, "T999")
        self.assertIsNone(result)

    def test_invalid_ticket_input_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets, "   ", "Network", "high", "12"
            )
    def test_ticket_creation_records_a_create_event_when_audit_data_is_given(self):
        events = []
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        ticket = create_ticket(
            self.tickets,
            "Wi-Fi is down",
            "Network",
            "high",
            "12",
            events=events,
            actor="Engineer B",
            now=now,
        )

        self.assertEqual(len(self.tickets), 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "CREATE")
        self.assertEqual(events[0]["ticket_id"], ticket["id"])
        self.assertEqual(events[0]["actor"], "Engineer B")
    def test_invalid_audit_actor_creates_neither_ticket_nor_event(self):
        events = []
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets,
                "Wi-Fi is down",
                "Network",
                "high",
                "12",
                events=events,
                actor="   ",
                now=now,
            )

        self.assertEqual(self.tickets, [])
        self.assertEqual(events, [])

    def test_duplicate_detection_normalizes_title_and_ignores_resolved_tickets(self):
        matching_ticket = create_ticket(
            self.tickets, " Wi-Fi   Down ", "Network", "high", "12"
        )
        resolved_ticket = create_ticket(
            self.tickets, "Wi-Fi Down", "Network", "low", "1"
        )
        resolved_ticket["status"] = "resolved"

        matches = detect_duplicates(self.tickets, " network ", "wi-fi down")

        self.assertEqual(matches, [matching_ticket])

if __name__ == "__main__":
    unittest.main()
