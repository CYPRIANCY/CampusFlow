## CampusFlow Design Decisions

1. Ownership
Area 	                                        Owner

Assignment, status workflow 	                Jacob Agera
JSON persistence 	                            Jacob Agera
Reports 	                                    Jacob Agera
Storage 	                                    Jacob Agera


Each fellow wrote their own tests alongside their code.
2. Shared data structure

    Tickets are stored as a list of dictionaries, passed explicitly to every function (no hidden global state).
    Functions find a ticket by looping through the list and matching ticket["id"].
    Trade-off: lookup is O(n), which is fine for a helpdesk of this size. A dictionary keyed by ID would be faster but would change the JSON shape and every function signature.

3. Error handling

    Business logic raises ValueError with a clear message (StorageError for file problems).
    Business logic never prints or calls input(). The CLI catches exceptions and displays the message.
    All validation happens before a ticket is modified, so rejected input never corrupts stored tickets.

4. Return values

    assign_ticket and change_status return the updated ticket dictionary.
    generate_report returns a dictionary; format_report turns it into text.
    load_tickets returns a list; save_tickets returns nothing.

5. Status workflow

Allowed: open -> in_progress, in_progress -> resolved, resolved -> open (reopen).

##Decisions

    An unassigned ticket cannot move to in_progress (from the brief).
    Skipping a step (open -> resolved) and going backwards (in_progress -> open) are rejected. The brief does not say either way, so we chose the stricter rule <CONFIRM with partner>.
    Resolved tickets cannot be reassigned until reopened.
    Implemented as a transitions dictionary (ALLOWED_TRANSITIONS) rather than chained if statements, so the rules are visible in one place and easy to change.

6. Normalization

    Ticket IDs, status names, category and urgency are trimmed and matched case-insensitively.
    Staff names are trimmed but keep their original capitalization.

7. Persistence

    campusflow/storage.py owns all JSON reading and writing. Other modules call save_tickets and load_tickets.
    Both functions take a path argument so tests can use a temporary folder and never touch real data.
    Missing file: return [] (fresh start).
    Malformed JSON: raise StorageError and leave the file untouched. Returning [] would let the next save silently erase the user's data.
    Saving writes a temporary file and then uses os.replace, so a crash mid-save cannot leave a half-written file.
    ID generation must look at loaded tickets (highest existing number plus 1) so IDs stay unique after reload in tickets.py.
    data/tickets.json is excluded from Git.

8. Reports

    generate_report always includes every known status and priority, with 0 when unused, so an empty list works without special cases.
    Calculation is separate from formatting so it can be tested without capturing printed output.

9. Testing approach

    unittest only (standard library).
    setUp creates fresh data for each test.
    Invalid input, boundaries and persistence are tested, not only the success path.
    Negative checks: temporarily break a rule, confirm the matching test fails, then restore it.
    Latest integrated result: 59 tests, all passing.

10. Git conventions

    Branch names: docs/design-decisions.md
    Every PR is reviewed and approved by the other fellow before merging.
    Merge conflicts in shared files (workflow.py, tests/test_workflow.py) are resolved by merging main into the feature branch, rerunning tests and pushing before final approval.

