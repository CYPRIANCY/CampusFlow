# AI Learning Log — CampusFlow Phase 2

## Cycle 1 — Storage Validation

### Question or confusion
How should CampusFlow handle duplicate ticket IDs, duplicate event IDs, and audit events that reference tickets that do not exist?

### AI explanation and critique
The guidance was to validate stored data before accepting it. Ticket IDs and event IDs should be present and unique, and every audit event should refer to an existing ticket. I needed to ensure these checks rejected corrupt data rather than silently replacing it.

### Independent experiment
I added a storage test for an event that references an unknown ticket ID. I ran the storage tests and then the full test suite to check that the new validation did not break existing behavior.

### Evidence
- Test command: `python3 -m unittest tests.test_storage -v`
- Full regression command: `python3 -m unittest discover -v`
- Actual full-suite result: `Ran 105 tests in 0.023s — OK`
- Formatting check: `git diff --check` completed without reporting errors.
- Files changed: `campusflow/storage.py`, `tests/test_storage.py`
- Commit or pull request: Add the verified commit or PR link when available.

### Decision
I kept the validation and added a test for an event referencing an unknown ticket. The test passed, providing evidence that this invalid reference is rejected. I also retained the existing tests for duplicate IDs and malformed JSON to check that the additional validation did not break those protections.

## Cycle 2 — SLA and Escalation

### Question or confusion
How should overdue tickets be identified, and how can repeated escalation checks avoid duplicate escalation events?

### AI explanation and critique
The proposed approach was to calculate deadlines from ticket priority, determine overdue status using the deadline and current time, and make escalation idempotent within an SLA cycle. The implementation also needed to preserve ticket workflow fields during escalation.

### Independent experiment
The project includes tests for priority-based SLA deadlines, overdue detection, repeated escalation checks, and whether escalation changes workflow fields. Review the test source and run the relevant tests to confirm the exact implementation and results.

### Evidence
- Test command: `python3 -m unittest tests.test_sla tests.test_escalation tests.test_sla_lifecycle -v`
- Full regression command: `python3 -m unittest discover -v`
- Actual full-suite result: `Ran 105 tests in 0.023s — OK`
- Files to verify: SLA, escalation, and lifecycle implementation files and their corresponding tests.
- Commit or pull request: Add the verified commit or PR link when available.

### Decision
The existing test suite passed tests covering SLA deadlines, overdue detection, escalation idempotency, and SLA lifecycle behavior. Before submission, I will inspect the implementation and test assertions to explain precisely how the current-cycle escalation rule works.

## Cycle 3 — Audit History and Data Integrity

### Question or confusion
How can rejected ticket actions leave both ticket state and audit history unchanged?

### AI explanation and critique
The proposed principle was to validate an action before changing ticket data or appending an audit event. I needed to check both the ticket fields and the event list rather than assuming that an error message alone proved the action had been rejected safely.

### Independent experiment
The workflow tests cover invalid actors, invalid status changes, assignment validation, and rejected transitions. I used the full test suite to check that these cases continued to pass.

### Evidence
- Test command: `python3 -m unittest tests.test_workflow tests.test_history -v`
- Full regression command: `python3 -m unittest discover -v`
- Actual full-suite result: `Ran 105 tests in 0.023s — OK`
- Files to verify: workflow and audit-history implementation files and their corresponding tests.
- Commit or pull request: Add the verified commit or PR link when available.

### Decision
The regression suite passed the existing tests for invalid actors and rejected workflow transitions. Before submission, I will review the relevant assertions to identify a specific rejected action and explain how the tests verify that both ticket state and audit history remain unchanged.

## Evidence and Submission Checklist

- [ ] Verify the exact SLA and escalation implementation.
- [ ] Inspect the relevant workflow tests and record one specific rejected-action example.
- [ ] Run the targeted commands recorded above and retain their actual output.
- [ ] Add verified commit hashes and pull request links.
- [ ] Document at least one example of AI advice that was independently tested and then modified or rejected because of evidence.
- [ ] Ensure the learning record reflects work I personally performed and can explain.
