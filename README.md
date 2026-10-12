# CampusFlow

CampusFlow is a lightweight, Python-based command-line helpdesk application for campus IT and support teams. It helps teams record reported issues, prioritize tickets, assign staff, track progress, and generate reports.

## The Problem

Campus support requests can arrive through email, WhatsApp, walk-ins, and other channels. This makes it difficult to identify urgent issues, determine who is responsible, and track unresolved requests.

CampusFlow provides a simple way to organize support tickets in one place.

## Features

- **Ticket creation:** Create tickets with a title, category, urgency, and number of affected users.
- **Input validation:** Reject invalid or incomplete ticket information.
- **Automatic priority calculation:** Calculate ticket priority using urgency and the number of affected users.
- **Ticket identification:** Generate unique ticket IDs such as `T001` and `T002`.
- **Ticket management:** List all tickets and view individual ticket details.
- **Staff assignment:** Assign tickets to staff members.
- **Status management:** Track tickets through `open`, `in_progress`, and `resolved` states, with support for reopening resolved tickets.
- **Priority queue:** Display unresolved tickets in priority order.
- **Reports:** View total ticket counts and breakdowns by status and priority.
- **JSON persistence:** Save tickets locally and reload them when the application restarts.
- **Automated testing:** Verify core functionality using Python's built-in `unittest` framework.

## Technology Stack

- Python 3.12.3
- Python standard library
- JSON for local data persistence
- `unittest` for automated testing
- Git and GitHub for version control and collaboration

## Requirements

- Python 3.12.3 or a compatible Python 3 version.
- Git, if you want to clone the repository.

The application uses Python's standard library for its core functionality.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/CYPRIANCY/CampusFlow.git
cd CampusFlow
```

### 2. Run the application

```bash
python3 main.py
```

On Windows, you may also use:

```bash
python main.py
```

### 3. Use the menu

The application provides options to:

1. Create a ticket.
2. List all tickets.
3. View ticket details.
4. Assign a ticket to a staff member.
5. Change a ticket's status.
6. View the priority queue.
7. View reports.
0. Save and exit.

Follow the prompts displayed in the terminal.

## Ticket Priority Rules

Priority is calculated from urgency and the number of affected users.

| Condition | Priority |
|---|---|
| High urgency and at least 10 affected users | Critical |
| High urgency or at least 10 affected users | High |
| Medium urgency or at least 3 affected users | Medium |
| None of the above | Low |

## Ticket Workflow

Tickets follow these transitions:

- `open` → `in_progress`
- `in_progress` → `resolved`
- `resolved` → `open` when a ticket needs to be reopened

A ticket must be assigned before it can move to `in_progress`.

## Data Storage

Ticket data is stored locally in `data/tickets.json`.

- The application starts with an empty ticket collection if the data file does not exist.
- Saved tickets are loaded when the application starts.
- Malformed or invalidly structured JSON is reported rather than silently treated as an empty collection.
- Runtime ticket data is excluded from version control.

## Running the Tests

Run the complete automated test suite from the project root:

```bash
python3 -m unittest discover -s tests -v
```

Check Python syntax with:

```bash
python3 -m py_compile main.py campusflow/*.py
```

## Project Structure

```text
CampusFlow/
├── campusflow/
│   ├── __init__.py
│   ├── assign_ticket.py
│   ├── queue.py
│   ├── reports.py
│   ├── storage.py
│   ├── tickets.py
│   └── workflow.py
├── docs/
│   └── design-decisions.md
├── tests/
│   ├── test_queue.py
│   ├── test_reports.py
│   ├── test_storage.py
│   ├── test_ticket_creation.py
│   ├── test_tickets.py
│   └── test_workflow.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Contributors

- AKPEN SESUGH CYPRIAN
- JACOB AGERA

## Contributing

1. Create a new branch for your change.
2. Make a focused change and add or update tests.
3. Run the automated test suite.
4. Commit and push your branch.
5. Open a pull request for review before merging.