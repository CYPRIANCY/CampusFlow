import unittest

from campusflow.workflow import assign_ticket


class TestAssignTicket(unittest.TestCase):
    def setUp(self):
        self.tickets = [
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


if __name__ == "__main__":
    unittest.main()