
import unittest

from campusflow.reports import format_report, generate_report, generate_sla_metrics


def make_ticket(ticket_id, status="open", priority="low"):
    return {
        "id": ticket_id,
        "title": "Sample",
        "category": "Other",
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": None,
    }


class TestGenerateReport(unittest.TestCase):
    def test_empty_list_gives_zero_report(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(sum(report["by_status"].values()), 0)
        self.assertEqual(sum(report["by_priority"].values()), 0)

    def test_total_counts_all_tickets(self):
        tickets = [make_ticket("T001"), make_ticket("T002"), make_ticket("T003")]
        self.assertEqual(generate_report(tickets)["total"], 3)

    def test_breakdown_by_status(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="open"),
            make_ticket("T003", status="in_progress"),
            make_ticket("T004", status="resolved"),
        ]
        by_status = generate_report(tickets)["by_status"]
        self.assertEqual(by_status["open"], 2)
        self.assertEqual(by_status["in_progress"], 1)
        self.assertEqual(by_status["resolved"], 1)

    def test_breakdown_by_priority(self):
        tickets = [
            make_ticket("T001", priority="critical"),
            make_ticket("T002", priority="high"),
            make_ticket("T003", priority="high"),
            make_ticket("T004", priority="low"),
        ]
        by_priority = generate_report(tickets)["by_priority"]
        self.assertEqual(by_priority["critical"], 1)
        self.assertEqual(by_priority["high"], 2)
        self.assertEqual(by_priority["medium"], 0)
        self.assertEqual(by_priority["low"], 1)

    def test_unused_categories_are_present_with_zero(self):
        report = generate_report([make_ticket("T001")])
        self.assertEqual(report["by_status"]["resolved"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)

    def test_breakdowns_add_up_to_total(self):
        tickets = [
            make_ticket("T001", status="open", priority="high"),
            make_ticket("T002", status="resolved", priority="medium"),
            make_ticket("T003", status="in_progress", priority="low"),
        ]
        report = generate_report(tickets)
        self.assertEqual(sum(report["by_status"].values()), report["total"])
        self.assertEqual(sum(report["by_priority"].values()), report["total"])

    def test_report_does_not_modify_tickets(self):
        tickets = [make_ticket("T001", status="open", priority="high")]
        before = [dict(t) for t in tickets]
        generate_report(tickets)
        self.assertEqual(tickets, before)

    def test_sla_metrics_are_read_only_and_do_not_double_count(self):
        tickets = [
            {
                **make_ticket("T001", status="open", priority="high"),
                "is_overdue": True,
                "escalation_cycle": 0,
                "escalated_cycle": 0,
            },
            {
                **make_ticket("T002", status="in_progress", priority="medium"),
                "is_overdue": False,
                "escalation_cycle": 1,
                "escalated_cycle": None,
            },
            {
                **make_ticket("T003", status="resolved", priority="low"),
                "is_overdue": True,
                "escalation_cycle": 0,
                "escalated_cycle": 0,
            },
        ]
        before = [dict(ticket) for ticket in tickets]

        metrics = generate_sla_metrics(
            tickets,
            now="fixed-test-time",
            overdue_checker=lambda ticket, now: ticket["is_overdue"],
        )

        self.assertEqual(metrics["open_count"], 1)
        self.assertEqual(metrics["in_progress_count"], 1)
        self.assertEqual(metrics["resolved_count"], 1)
        self.assertEqual(metrics["overdue_unresolved_count"], 1)
        self.assertEqual(metrics["escalated_in_current_cycle_count"], 2)
        self.assertEqual(metrics["by_priority"]["high"], 1)
        self.assertEqual(tickets, before)


class TestFormatReport(unittest.TestCase):
    def test_format_shows_total_and_sections(self):
        text = format_report(generate_report([make_ticket("T001")]))
        self.assertIn("Total tickets: 1", text)
        self.assertIn("By status:", text)
        self.assertIn("By priority:", text)

    def test_format_empty_report(self):
        text = format_report(generate_report([]))
        self.assertIn("Total tickets: 0", text)
        self.assertIn("open: 0", text)


if __name__ == "__main__":
    unittest.main()
