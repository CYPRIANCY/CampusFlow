"""Question bank and pure scoring helpers for the Engineering Knowledge Lab."""

from datetime import datetime, timezone
import json
import os
import tempfile


VALID_CHOICES = {"A", "B", "C", "D"}
DEFAULT_SESSION_PATH = os.path.join("data", "learning-sessions.json")

QUESTIONS = [
    {
        "topic": "SLA boundary",
        "prompt": "A critical ticket is created at 10:00 UTC. At 11:00 UTC, is it overdue?",
        "options": [
            "A Yes",
            "B No, only strictly after 11:00",
            "C Only if assigned",
            "D Only if reopened",
        ],
        "correct_answer": "B",
    },
    {
        "topic": "priority matrix",
        "prompt": "urgency=low and affected_users=10. What priority?",
        "options": ["A Critical", "B High", "C Medium", "D Low"],
        "correct_answer": "B",
    },
    {
        "topic": "workflow invariant",
        "prompt": "An unassigned open ticket moves directly to in_progress. What should happen?",
        "options": [
            "A Transition succeeds",
            "B Status changes but history stays",
            "C Reject without changing ticket or events",
            "D Delete the ticket",
        ],
        "correct_answer": "C",
    },
    {
        "topic": "SLA cycle",
        "prompt": "A resolved high-priority ticket is reopened. Which SLA behavior is correct?",
        "options": [
            "A Keep old due_at always",
            "B Start a fresh SLA cycle while preserving created_at",
            "C Reset created_at to today",
            "D Delete previous events",
        ],
        "correct_answer": "B",
    },
    {
        "topic": "idempotency",
        "prompt": "An overdue ticket is checked three times in one SLA cycle. How many new ESCALATE events?",
        "options": ["A Three", "B Two", "C One", "D Zero"],
        "correct_answer": "C",
    },
    {
        "topic": "JSON integrity",
        "prompt": "The saved file has invalid JSON. What is the safest action?",
        "options": [
            "A Replace data with empty list",
            "B Use eval()",
            "C Keep partial data",
            "D Reject load and preserve existing valid state",
        ],
        "correct_answer": "D",
    },
    {
        "topic": "code review",
        "prompt": "A PR changes SLA calculations but adds no boundary tests. What should a reviewer do?",
        "options": [
            "A Approve because it runs locally",
            "B Request focused tests and explanation",
            "C Merge and test next week",
            "D Ask AI to approve automatically",
        ],
        "correct_answer": "B",
    },
    {
        "topic": "AI verification",
        "prompt": "An assistant says use eval() to parse stored JSON. What should you do?",
        "options": [
            "A Copy it",
            "B Disable tests",
            "C Reject it and use JSON parsing with validation",
            "D Share the whole file publicly",
        ],
        "correct_answer": "C",
    },
    {
        "topic": "duplicate warning",
        "prompt": "Matching normalized titles share a category and are unresolved. What should the CLI do?",
        "options": [
            "A Silently delete original",
            "B Warn and require confirmation",
            "C Silently block forever",
            "D Ignore normalization",
        ],
        "correct_answer": "B",
    },
    {
        "topic": "audit integrity",
        "prompt": "An invalid return/status operation is rejected. What happens to event count?",
        "options": ["A Increase by one", "B Increase twice", "C Reset to zero", "D Stay unchanged"],
        "correct_answer": "D",
    },
]


def prompt_choice(prompt, input_fn=input, output_fn=print):
    """Prompt repeatedly until the user enters an exact A/B/C/D answer."""
    while True:
        choice = input_fn(prompt)
        if choice in VALID_CHOICES:
            return choice
        output_fn("Invalid input. Enter exactly A, B, C, or D.")


def run_knowledge_lab(input_fn=input, output_fn=print, session_path=DEFAULT_SESSION_PATH, now=None):
    """Run the interactive quiz and save a separate learning-session record."""
    participant = ""
    while participant not in {"A", "B"}:
        participant = input_fn("Participant (A/B): ")
        if participant not in {"A", "B"}:
            output_fn("Invalid input. Enter exactly A or B.")

    choices = []
    explanations = {}
    for index, question in enumerate(QUESTIONS, start=1):
        output_fn(f"\nQ{index}. {question['prompt']}")
        for option in question["options"]:
            output_fn(option)
        choices.append(prompt_choice("Answer (A/B/C/D): ", input_fn, output_fn))
        explanation = input_fn("Explanation (optional for now): ").strip()
        if explanation:
            explanations[f"Q{index}"] = explanation

    for index in range(1, len(QUESTIONS) + 1):
        if len(explanations) >= 3:
            break
        key = f"Q{index}"
        if key not in explanations:
            explanation = input_fn(f"Explanation required for {key}: ").strip()
            while not explanation:
                output_fn("An explanation is required.")
                explanation = input_fn(f"Explanation required for {key}: ").strip()
            explanations[key] = explanation

    session_time = datetime.now(timezone.utc) if now is None else now
    session = build_session(participant, choices, explanations, session_time)
    save_learning_session(session, session_path)

    output_fn(f"\nScore: {session['score']}/10")
    output_fn("Answers: " + ", ".join(session["choices"]))
    if session["revision_topics"]:
        output_fn("Topics to revise: " + ", ".join(session["revision_topics"]))
    else:
        output_fn("Topics to revise: none")
    output_fn("Explanations:")
    for key, explanation in session["explanations"].items():
        output_fn(f"  {key}: {explanation}")
    return session


def score_choices(choices):
    """Score ten exact multiple-choice answers and list topics to revise."""
    if not isinstance(choices, list) or len(choices) != len(QUESTIONS):
        raise ValueError("Exactly ten choices are required.")
    if any(choice not in VALID_CHOICES for choice in choices):
        raise ValueError("Each choice must be exactly A, B, C, or D.")

    revision_topics = []
    score = 0
    for choice, question in zip(choices, QUESTIONS):
        if choice == question["correct_answer"]:
            score += 1
        else:
            revision_topics.append(question["topic"])
    return {"score": score, "revision_topics": revision_topics}


def build_session(participant, choices, explanations, now):
    """Build one validated, ticket-independent Knowledge Lab session record."""
    if participant not in {"A", "B"}:
        raise ValueError("Participant must be A or B.")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Session time must be timezone-aware.")
    if not isinstance(explanations, dict):
        raise ValueError("Explanations must be stored as a dictionary.")

    non_empty_explanations = {
        key: value.strip()
        for key, value in explanations.items()
        if isinstance(value, str) and value.strip()
    }
    if len(non_empty_explanations) < 3:
        raise ValueError("At least three explanations are required.")

    result = score_choices(choices)
    return {
        "participant": participant,
        "timestamp": now.astimezone(timezone.utc).isoformat(),
        "choices": list(choices),
        "score": result["score"],
        "revision_topics": result["revision_topics"],
        "explanations": non_empty_explanations,
    }


def save_learning_session(session, path):
    """Append one session to its separate JSON file using an atomic replace."""
    if not isinstance(session, dict):
        raise ValueError("Learning session must be a dictionary.")

    sessions = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as saved_file:
                sessions = json.load(saved_file)
        except json.JSONDecodeError as error:
            raise ValueError("Learning-session file is not valid JSON.") from error
        if not isinstance(sessions, list):
            raise ValueError("Learning-session file must contain a list.")

    sessions.append(session)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    descriptor, temporary_path = tempfile.mkstemp(dir=folder or ".", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary_file:
            json.dump(sessions, temporary_file, indent=2)
        os.replace(temporary_path, path)
    except Exception:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise
