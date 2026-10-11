## AI Learning LogFellow: Jacob Agera Interaction 

##1: Writing tests with unittest and proving a test can fail 

Problem: I needed to test assign_ticket, including that invalid input is rejected and the ticket is left unchanged.

My initial understanding: I knew a test calls a function and checks the result, but not how to check that an error is raised.

Prompt to AI: "Help me test my assign function. Explain assertRaises. Do not write the whole project all i need is a psuedocode.

Useful AI guidance: assertRaises as a context manager checks that a specific exception occurs. setUp gives every test a fresh ticket so tests cannot affect each other. A test that has never failed has not proved anything.

My independent experiment/test: I wrote tests for a valid assignment, trimmed name, unknown ID, blank name, resolved ticket and reassignment. My first run failed with AssertionError: ValueError not raised because the function body was not finished. After completing it, all tests passed. I then ran a negative check by temporarily removing the resolved-ticket check and confirmed test_resolved_ticket_rejected failed.

Verification source or result: python3 -m unittest tests.test_workflow.TestAssignTicket -v showed 6 tests, all ok.

Decision: Accepted. I kept the tests because they each have a clear assertion and one of them checks that the ticket is unchanged after a rejection.

Related file/commit: tests/test_workflow.py, branch feat/<number>-ticket-assignment, commit <SHA>

What I can now explain without AI: "assertRaises passes only if the code raises the exception. If nothing is raised the test fails, which is how I know the validation really exists.

##Interaction 2: Validate before you modify (status workflow design)Problem: I needed change_status to enforce open -> in_progress -> resolved, block unassigned tickets from starting work, and never leave a ticket half-changed.

My initial understanding: "I planned a chain of if statements that changed the status as it went.

Prompt to AI: I am working on a Python-based ticket management system called CampusFlow. Help me understand how to implement a change_status() function using a chain of if statements. The function should validate ticket status transitions, ensure that only permitted transitions are allowed, and prevent an unassigned ticket from moving to in_progress. Please explain the logic step by step, show me how to handle invalid transitions, and help me with the psuedocode in a way that follows the project's existing structure and requirements.

Useful AI guidance: Use a dictionary of allowed transitions instead of chained if statements, and run every check before the single line that changes the ticket. The unassigned check comes after the transition check.

My independent experiment/test: I ran a manual script that called change_status in sequence and predicted each result before running it (unassigned to in_progress rejected, skip to resolved rejected, assigned to in_progress ok, in_progress to open rejected, resolved, reopen ok, invalid status rejected). I also added test_in_progress_cannot_go_back_to_open and checked it failed when I temporarily allowed that move. 

Verification source or result: python3 -m unittest tests.test_workflow.TestChangeStatus -v showed 9 tests, all ok.Decision: Accepted the transitions dictionary. Rejecting skipped steps (open -> resolved) was my team's stricter choice because the brief does not say. I asked my partner to confirm it in the PR. 

Related file/commit: campusflow/workflow.py, tests/test_workflow.py, commit eadb3d4

What I can now explain without AI: Why validation happens before modification (so a rejected call can never corrupt a ticket), and why a transitions table is easier to read and change than nested ifs.

Interaction 3: Reading tracebacks and correcting an AI-suggested method (corrected suggestion)

Problem: After adding change_status, my tests failed with errors I did not understand, and later my files stopped importing.

My initial understanding: "I thought the error meant my logic was wrong.

Prompt to AI: I encountered an error while implementing my Python code, and I initially thought the problem was with my logic. Help me understand what the error means, identify whether it is caused by incorrect logic, syntax, indentation, or another issue, and explain how to debug and fix it step by step without rewriting the entire code for me.

Useful AI guidance: Read the last line of a traceback first. NameError: name 'VALID_STATUSES' is not defined meant the constant was missing from the file, and grep -n confirmed it. IndentationError: unexpected indent and NameError: name 'cat' is not defined pointed to damaged file contents.

My independent experiment/test: I used grep -n, wc -l and python3 -c "import campusflow.workflow" to inspect the real files. The checks showed VALID_STATUSES defined twice, the file much longer than expected (99 and 101 lines), and the literal text cat > campusflow/workflow.py << 'EOF' and a stray EOF line inside both workflow.py and test_workflow.py.

Verification source or result: The AI had given me terminal cat > file << 'EOF' blocks to write whole files. I pasted them into the editor instead of the terminal, so the shell commands became part of my Python files. I deleted the junk lines with sed -i and confirmed with grep -n "cat >\|EOF" (no output), a clean import, and a full passing test run.

Decision: Corrected. The AI's instructions were correct for a terminal, but I should not have trusted a method I had not checked in my environment. Afterwards I verified every pasted file with grep for leftover cat > and EOF and with an import check before running tests. 

Related file/commit: campusflow/workflow.py, tests/test_workflow.py, campusflow/storage.py, tests/test_storage.py

What I can now explain without AI: How to read a traceback from the bottom up, how grep and wc -l show what is really in a file, and why I check pasted code before running it.

Interaction 4 (optional): JSON persistence and failing safely

Problem: I needed save_tickets and load_tickets so tickets survive a restart and a corrupted file never erases data.

My initial understanding: <your words>Prompt to AI: <your actual prompt>Useful AI guidance: A missing file means a fresh start ([]), but malformed JSON must raise StorageError, because returning [] would let the next save overwrite the user's data. Write to a temporary file and then os.replace so a crash cannot leave a half-written file. Take a path argument so tests use a temporary folder.

My independent experiment/test: I ran a script using a temporary directory and predicted each result: missing file gives [], round trip is identical, None survives as None, corrupt file raises StorageError and is left untouched, wrong shape is rejected, no temp files remain. 


Verification source or result: python3 -m unittest tests.test_storage -v showed 8 tests, all ok. Negative check: changing the malformed-JSON raise to return [] made the test fail. 

Decision: Accepted.

Related file/commit: campusflow/storage.py, tests/test_storage.py, commit <SHA>

What I can now explain without AI: Why failing loudly is safer than returning an empty list, and why the temp-file swap protects the data.

Interaction 5 (optional): Separating calculation from formatting (reports)Problem: I needed reports that work with zero tickets and can be tested without capturing printed output.

Prompt to AI: I am working on the CampusFlow ticket management system in Python. I need to implement reporting functions that work correctly even when there are zero tickets in the system. Please guide me on how to handle empty ticket lists without causing errors and how to structure the reporting functions so they return data instead of printing directly to the terminal. Explain how I can write unit tests to verify the report results, including when the ticket list is empty, without having to capture printed output. Please explain the approach step by step and help me understand the reasoning behind it rather than rewriting the entire code for me.Useful 

AI guidance: Have generate_report return a dictionary and format_report turn it into text. Pre-fill every status and priority with 0 so an empty list needs no special case.

My independent experiment/test: I ran a manual script with predicted output for an empty list and for three tickets, then a negative check by setting total to 0 and watching test_total_counts_all_tickets and test_breakdowns_add_up_to_total fail.Verification source or result: Ran 9 tests ... OK for test_reports, and Ran 59 tests ... OK for the full suite.

Decision: Accepted.

Related file/commit: campusflow/reports.py, tests/test_reports.py

What I can now explain without AI: Why separating logic from display makes code easier to test.


Individual reflection: Jacob Agera

##1. Which feature did you personally implement, and how do you know it works?I implemented assignment, the status workflow, JSON persistence and reports. I know they work because each has automated tests with assertions for normal, invalid and boundary cases, the full suite shows Ran 59 tests ... OK, and I did negative checks where breaking a rule made the matching test fail.

##2. What did AI teach you that you did not understand at the start?  validating before modifying, assertRaises, why malformed JSON must raise

##3. Give one example where you verified, changed, or rejected an AI suggestion. see Interaction #3

##4. What did you learn from reviewing your partner's PR? Reviewing my partner's pull request taught me the importance of checking code correctness, readability, and edge cases before approving changes. I learned to look beyond whether the code runs and consider whether it handles invalid inputs and unexpected situations correctly. I also learned how to provide constructive feedback and suggest improvements without unnecessarily changing my partner's implementation. The review helped me understand that code reviews are essential for maintaining code quality, preventing bugs, and ensuring that new features integrate properly with the existing project.

##5. What would you improve next if the team had another hour? a staff directory, ticket editing, search, an audit log of status changes.