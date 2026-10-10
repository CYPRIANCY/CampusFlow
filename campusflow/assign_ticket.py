    def test_valid_assignment(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_name_is_trimmed(self):
        assign_ticket(self.tickets, "t001", "  Ada  ")
        self.assertEqual(self.tickets[0]["assigned_to"], "Ada")

    def test_blank_name_rejected_and_ticket_unchanged(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_resolved_ticket_rejected(self):
        self.tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")