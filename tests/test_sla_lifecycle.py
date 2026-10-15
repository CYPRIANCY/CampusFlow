
import unittest
from datetime import datetime, timezone, timedelta

from campusflow.tickets import create_ticket
from campusflow.workflow import change_status


class TestSLALifecycle(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        self.start_time = datetime(
            2026, 10, 15, 8, 0, tzinfo=timezone.utc
        )

    def test_new_ticket_has_sla_fields(self):
        ticket = create_ticket(
            self.tickets,
            "Internet unavailable",
            "network",
            "high",
            5,
            now=self.start_time,
        )

        self.assertEqual(ticket["created_at"], self.start_time.isoformat())
        self.assertEqual(ticket["updated_at"], self.start_time.isoformat())
        self.assertEqual(ticket["escalation_cycle"], 0)
        self.assertIsNone(ticket["escalated_cycle"])

        due_at = datetime.fromisoformat(ticket["due_at"])
        self.assertEqual(
            due_at,
            self.start_time + timedelta(minutes=240),
        )

    def test_reopening_starts_a_new_sla_cycle(self):
        ticket = create_ticket(
            self.tickets,
            "Internet unavailable",
            "network",
            "high",
            5,
            now=self.start_time,
        )

        original_created_at = ticket["created_at"]
        original_due_at = ticket["due_at"]

        ticket["assigned_to"] = "Ada"

        change_status(
            self.tickets,
            ticket["id"],
            "in_progress",
            now=self.start_time + timedelta(minutes=10),
        )
        change_status(
            self.tickets,
            ticket["id"],
            "resolved",
            now=self.start_time + timedelta(minutes=20),
        )

        ticket["escalated_cycle"] = 0

        reopened_at = self.start_time + timedelta(hours=2)
        change_status(
            self.tickets,
            ticket["id"],
            "open",
            now=reopened_at,
        )

        self.assertEqual(ticket["created_at"], original_created_at)
        self.assertEqual(ticket["updated_at"], reopened_at.isoformat())
        self.assertEqual(ticket["escalation_cycle"], 1)
        self.assertIsNone(ticket["escalated_cycle"])
        self.assertNotEqual(ticket["due_at"], original_due_at)

        expected_due_at = reopened_at + timedelta(minutes=240)
        self.assertEqual(
            datetime.fromisoformat(ticket["due_at"]),
            expected_due_at,
        )


if __name__ == "__main__":
    unittest.main()
