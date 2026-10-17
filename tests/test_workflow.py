import unittest
from datetime import datetime, timezone

from campusflow.workflow import assign_ticket, change_status


def make_tickets():
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
        }
    ]


class TestAssignTicket(unittest.TestCase):
    def setUp(self):
        self.tickets = make_tickets()

    def test_valid_assignment(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_name_is_trimmed(self):
        assign_ticket(self.tickets, "t001", "  Ada  ")
        self.assertEqual(self.tickets[0]["assigned_to"], "Ada")

    def test_unknown_id_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T999", "Ada")

    def test_blank_name_rejected_and_ticket_unchanged(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_resolved_ticket_rejected(self):
        self.tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")

    def test_reassigning_open_ticket_updates_name(self):
        assign_ticket(self.tickets, "T001", "Ada")
        assign_ticket(self.tickets, "T001", "Bola")
        self.assertEqual(self.tickets[0]["assigned_to"], "Bola")

    def test_valid_assignment_records_an_assign_event(self):
        events = []
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

        ticket = assign_ticket(
            self.tickets,
            "T001",
            "Ada",
            events=events,
            actor="Engineer B",
            now=now,
        )

        self.assertEqual(ticket["assigned_to"], "Ada")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "ASSIGN")
        self.assertEqual(events[0]["ticket_id"], "T001")
        self.assertEqual(events[0]["before_status"], "open")
        self.assertEqual(events[0]["after_status"], "open")


class TestChangeStatus(unittest.TestCase):
    def setUp(self):
        self.tickets = make_tickets()

    def test_unassigned_ticket_cannot_start(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_full_lifecycle(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "in_progress")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_cannot_skip_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_reopen_resolved_ticket(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        change_status(self.tickets, "T001", "open")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_resolved_cannot_jump_to_in_progress(self):
        self.tickets[0]["assigned_to"] = "Ada"
        self.tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_in_progress_cannot_go_back_to_open(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "open")
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "done")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_invalid_actor_leaves_ticket_and_events_unchanged(self):
        assign_ticket(self.tickets, "T001", "Ada")
        events = []
        original_ticket = self.tickets[0].copy()

        with self.assertRaises(ValueError):
            change_status(
                self.tickets,
                "T001",
                "in_progress",
                events=events,
                actor="   ",
            )

        self.assertEqual(self.tickets[0], original_ticket)
        self.assertEqual(events, [])

    def test_unknown_id_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T999", "in_progress")

    def test_status_is_case_insensitive(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "t001", "  IN_PROGRESS ")
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_successful_status_changes_record_start_resolve_and_reopen_events(self):
        events = []
        now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
        assign_ticket(self.tickets, "T001", "Ada")

        change_status(
            self.tickets, "T001", "in_progress",
            events=events, actor="Engineer B", now=now,
        )
        change_status(
            self.tickets, "T001", "resolved",
            events=events, actor="Engineer B", now=now,
        )
        change_status(
            self.tickets, "T001", "open",
            events=events, actor="Engineer B", now=now,
        )

        self.assertEqual(
            [event["event_type"] for event in events],
            ["START", "RESOLVE", "REOPEN"],
        )
        self.assertEqual(self.tickets[0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
