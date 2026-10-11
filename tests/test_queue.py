
import unittest

from campusflow.queue import get_ticket_queue


class TestTicketQueue(unittest.TestCase):

    def test_priority_order(self):
        tickets = [
            {"id": "T001", "priority": "low", "status": "open"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T003", "priority": "high", "status": "open"},
        ]

        result = get_ticket_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T002", "T003", "T001"]
        )

    def test_same_priority_uses_numeric_id(self):
        tickets = [
            {"id": "T010", "priority": "critical", "status": "open"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T001", "priority": "critical", "status": "open"},
        ]

        result = get_ticket_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T002", "T010"]
        )

    def test_resolved_tickets_are_excluded(self):
        tickets = [
            {"id": "T001", "priority": "critical", "status": "resolved"},
            {"id": "T002", "priority": "low", "status": "open"},
        ]

        result = get_ticket_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T002"]
        )

    def test_empty_queue(self):
        self.assertEqual(get_ticket_queue([]), [])

    def test_original_list_is_not_reordered(self):
        tickets = [
            {"id": "T002", "priority": "low", "status": "open"},
            {"id": "T001", "priority": "critical", "status": "open"},
        ]
        original_ids = [ticket["id"] for ticket in tickets]

        get_ticket_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in tickets],
            original_ids
        )


if __name__ == "__main__":
    unittest.main()
