
STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")


def generate_report(tickets):
    """Return a summary of the tickets as a dictionary.

    {
        "total": int,
        "by_status": {"open": n, "in_progress": n, "resolved": n},
        "by_priority": {"critical": n, "high": n, "medium": n, "low": n},
    }

    Every known status and priority is always present, with 0 when
    there are no matching tickets, so an empty list still works.
    """
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    """Turn a report dictionary into text the CLI can print."""
    lines = ["=== CampusFlow Report ===", f"Total tickets: {report['total']}", ""]
    lines.append("By status:")
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    return "\n".join(lines)
