
import unittest
from datetime import datetime, timezone

from campusflow.sla import calculate_due_at, is_overdue


class TestSLA(unittest.TestCase):

    def setUp(self):
        self.start_time = datetime(
            2026, 10, 14, 10, 0, tzinfo=timezone.utc
        )

    def test_critical_deadline_is_60_minutes(self):
        due_at = calculate_due_at("Critical", self.start_time)

        self.assertEqual(
            due_at,
            "2026-10-14T11:00:00+00:00"
        )

    def test_high_deadline_is_four_hours(self):
        due_at = calculate_due_at("High", self.start_time)

        self.assertEqual(
            due_at,
            "2026-10-14T14:00:00+00:00"
        )

    def test_medium_deadline_is_24_hours(self):
        due_at = calculate_due_at("Medium", self.start_time)

        self.assertEqual(
            due_at,
            "2026-10-15T10:00:00+00:00"
        )

    def test_low_deadline_is_48_hours(self):
        due_at = calculate_due_at("Low", self.start_time)

        self.assertEqual(
            due_at,
            "2026-10-16T10:00:00+00:00"
        )

    def test_critical_ticket_not_overdue_at_exact_deadline(self):
        ticket = {
            "status": "open",
            "due_at": "2026-10-14T11:00:00+00:00"
        }
        now = datetime(
            2026, 10, 14, 11, 0, tzinfo=timezone.utc
        )

        self.assertFalse(is_overdue(ticket, now))

    def test_critical_ticket_overdue_one_minute_after_deadline(self):
        ticket = {
            "status": "open",
            "due_at": "2026-10-14T11:00:00+00:00"
        }
        now = datetime(
            2026, 10, 14, 11, 1, tzinfo=timezone.utc
        )

        self.assertTrue(is_overdue(ticket, now))

    def test_resolved_ticket_is_not_overdue(self):
        ticket = {
            "status": "resolved",
            "due_at": "2026-10-14T11:00:00+00:00"
        }
        now = datetime(
            2026, 10, 14, 12, 0, tzinfo=timezone.utc
        )

        self.assertFalse(is_overdue(ticket, now))

    def test_naive_current_time_is_rejected(self):
        ticket = {
            "status": "open",
            "due_at": "2026-10-14T11:00:00+00:00"
        }
        now = datetime(2026, 10, 14, 12, 0)

        with self.assertRaises(ValueError):
            is_overdue(ticket, now)


if __name__ == "__main__":
    unittest.main()
