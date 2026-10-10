import unittest

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

    def test_unknown_id_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T999", "in_progress")

    def test_status_is_case_insensitive(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "t001", "  IN_PROGRESS ")
        self.assertEqual(self.tickets[0]["status"], "in_progress")


if __name__ == "__main__":
    unittest.main()
