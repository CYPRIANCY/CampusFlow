import unittest
from datetime import datetime, timezone

from campusflow.history import append_event, format_history, history_for_ticket

class TestAuditHistory(unittest.TestCase):
    def test_create_event_contains_required_fields(self):
        events = []
        ticket = {"id": "T001", "status": "open"}
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        event = append_event(
            events=events,
            ticket=ticket,
            event_type="CREATE",
            actor="Engineer B",
            before_status="open",
            after_status="open",
            details="Ticket created.",
            now=now,
        )

        self.assertEqual(event["event_id"], "E0001")
        self.assertEqual(event["ticket_id"], "T001")
        self.assertEqual(event["event_type"], "CREATE")
        self.assertEqual(event["actor"], "Engineer B")
        self.assertEqual(event["timestamp"], "2026-10-14T10:00:00+00:00")
        self.assertEqual(event["before_status"], "open")
        self.assertEqual(event["after_status"], "open")
        self.assertEqual(event["details"], "Ticket created.")
        self.assertEqual(events, [event])

    def test_invalid_actor_does_not_append_an_event(self):
        events = []
        ticket = {"id": "T001", "status": "open"}
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        with self.assertRaises(ValueError):
            append_event(
                events=events,
                ticket=ticket,
                event_type="CREATE",
                actor="   ",
                before_status="open",
                after_status="open",
                details="Ticket created.",
                now=now,
            )

        self.assertEqual(events, [])

    def test_second_event_gets_the_next_id(self):
        events = []
        ticket = {"id": "T001", "status": "open"}
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        append_event(
            events=events,
            ticket=ticket,
            event_type="CREATE",
            actor="Engineer B",
            before_status="open",
            after_status="open",
            details="Ticket created.",
            now=now,
        )

        second_event = append_event(
            events=events,
            ticket=ticket,
            event_type="ASSIGN",
            actor="Engineer B",
            before_status="open",
            after_status="open",
            details="Assigned to Ada.",
            now=now,
        )

        self.assertEqual(second_event["event_id"], "E0002")
        self.assertEqual(len(events), 2)

    def test_event_id_uses_the_highest_existing_number(self):
        events = [{"event_id": "E0007"}]
        ticket = {"id": "T001", "status": "open"}
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        event = append_event(
            events, ticket, "CREATE", "Engineer B", "open", "open",
            "Ticket created.", now,
        )

        self.assertEqual(event["event_id"], "E0008")

    def test_history_for_ticket_filters_and_orders_tied_timestamps(self):
        events = [
            {
                "event_id": "E0003",
                "ticket_id": "T001",
                "timestamp": "2026-10-14T10:00:00+00:00",
            },
            {
                "event_id": "E0001",
                "ticket_id": "T001",
                "timestamp": "2026-10-14T10:00:00+00:00",
            },
            {
                "event_id": "E0002",
                "ticket_id": "T002",
                "timestamp": "2026-10-14T09:00:00+00:00",
            },
        ]

        result = history_for_ticket(events, " t001 ")

        self.assertEqual(
            [event["event_id"] for event in result],
            ["E0001", "E0003"],
        )

    def test_format_history_shows_a_readable_chronological_entry(self):
        events = []
        ticket = {"id": "T001", "status": "open"}
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
        append_event(
            events, ticket, "CREATE", "Engineer B", "open", "open",
            "Ticket created.", now,
        )

        text = format_history(events, "T001")

        self.assertIn("History for T001", text)
        self.assertIn("E0001 | CREATE | open -> open", text)
        self.assertIn("Engineer B: Ticket created.", text)


if __name__ == "__main__":
    unittest.main()
