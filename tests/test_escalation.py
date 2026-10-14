
import unittest
from datetime import datetime, timezone

from campusflow.escalation import escalate_overdue


class TestEscalation(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 10, 14, 12, 1, tzinfo=timezone.utc
        )

        self.tickets = [
            {
                "id": "T001",
                "priority": "Critical",
                "status": "open",
                "assigned_to": "Ada",
                "due_at": "2026-10-14T11:00:00+00:00",
                "escalation_cycle": 0,
                "escalated_cycle": None,
            },
            {
                "id": "T002",
                "priority": "High",
                "status": "resolved",
                "assigned_to": "Ben",
                "due_at": "2026-10-14T11:00:00+00:00",
                "escalation_cycle": 0,
                "escalated_cycle": None,
            },
            {
                "id": "T003",
                "priority": "Low",
                "status": "open",
                "assigned_to": None,
                "due_at": "2026-10-14T13:00:00+00:00",
                "escalation_cycle": 0,
                "escalated_cycle": None,
            },
        ]

        self.events = []

    def test_escalates_overdue_ticket_once(self):
        result = escalate_overdue(
            self.tickets, self.events, self.now, "Cyprian"
        )

        self.assertEqual(result["newly_escalated"], 1)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0]["event_type"], "ESCALATE")
        self.assertEqual(self.events[0]["ticket_id"], "T001")

    def test_repeated_check_does_not_duplicate_event(self):
        first = escalate_overdue(
            self.tickets, self.events, self.now, "Cyprian"
        )
        second = escalate_overdue(
            self.tickets, self.events, self.now, "Cyprian"
        )

        self.assertEqual(first["newly_escalated"], 1)
        self.assertEqual(second["newly_escalated"], 0)
        self.assertEqual(second["already_escalated"], 1)
        self.assertEqual(len(self.events), 1)

    def test_resolved_and_not_due_tickets_are_not_escalated(self):
        escalate_overdue(
            self.tickets, self.events, self.now, "Cyprian"
        )

        escalated_ids = [
            event["ticket_id"] for event in self.events
        ]

        self.assertNotIn("T002", escalated_ids)
        self.assertNotIn("T003", escalated_ids)

    def test_escalation_does_not_change_ticket_workflow_fields(self):
        ticket = self.tickets[0]
        original = {
            key: ticket[key]
            for key in ("status", "priority", "assigned_to")
        }

        escalate_overdue(
            self.tickets, self.events, self.now, "Cyprian"
        )

        for key, value in original.items():
            self.assertEqual(ticket[key], value)


if __name__ == "__main__":
    unittest.main()
