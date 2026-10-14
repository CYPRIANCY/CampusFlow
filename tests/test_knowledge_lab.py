import unittest
from datetime import datetime, timezone
import json
import os
import tempfile
from unittest.mock import patch

from campusflow.knowledge_lab import (
    QUESTIONS,
    build_session,
    prompt_choice,
    run_knowledge_lab,
    save_learning_session,
    score_choices,
)


class TestKnowledgeLab(unittest.TestCase):
    def test_prompt_choice_reprompts_invalid_answer(self):
        answers = iter(["E", "B"])
        messages = []

        result = prompt_choice(
            "Answer: ", input_fn=lambda prompt: next(answers), output_fn=messages.append
        )

        self.assertEqual(result, "B")
        self.assertEqual(messages, ["Invalid input. Enter exactly A, B, C, or D."])

    def test_question_bank_contains_the_required_ten_questions(self):
        self.assertEqual(len(QUESTIONS), 10)
        self.assertEqual(
            [question["correct_answer"] for question in QUESTIONS],
            ["B", "B", "C", "B", "C", "D", "B", "C", "B", "D"],
        )

    def test_score_choices_returns_score_and_revision_topics(self):
        result = score_choices(["B", "A", "C", "B", "C", "D", "A", "C", "B", "D"])

        self.assertEqual(result["score"], 8)
        self.assertEqual(result["revision_topics"], ["priority matrix", "code review"])

    def test_score_choices_rejects_invalid_or_incomplete_answers(self):
        with self.assertRaises(ValueError):
            score_choices(["B"] * 9)
        with self.assertRaises(ValueError):
            score_choices(["B"] * 9 + ["E"])

    def test_build_session_requires_three_explanations_and_keeps_quiz_data(self):
        now = datetime(2026, 10, 15, 9, 0, tzinfo=timezone.utc)
        choices = [question["correct_answer"] for question in QUESTIONS]
        explanations = {
            "Q1": "Due is the deadline; overdue begins strictly after it.",
            "Q5": "Idempotency prevents duplicate escalation events.",
            "Q10": "Rejected operations must not leave audit records.",
        }

        session = build_session("B", choices, explanations, now)

        self.assertEqual(session["participant"], "B")
        self.assertEqual(session["timestamp"], "2026-10-15T09:00:00+00:00")
        self.assertEqual(session["score"], 10)
        self.assertEqual(session["choices"], choices)
        self.assertEqual(session["explanations"], explanations)

    def test_save_learning_session_writes_a_separate_json_record(self):
        now = datetime(2026, 10, 15, 9, 0, tzinfo=timezone.utc)
        choices = [question["correct_answer"] for question in QUESTIONS]
        session = build_session(
            "A", choices,
            {"Q1": "One.", "Q2": "Two.", "Q3": "Three."}, now,
        )
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "learning-sessions.json")
            save_learning_session(session, path)
            with open(path, "r", encoding="utf-8") as saved_file:
                self.assertEqual(json.load(saved_file), [session])

    def test_interactive_lab_scores_and_saves_without_ticket_state(self):
        answers = ["B"]
        for index, question in enumerate(QUESTIONS, start=1):
            answers.append(question["correct_answer"])
            answers.append(f"Explanation {index}." if index <= 3 else "")
        responses = iter(answers)
        output = []
        now = datetime(2026, 10, 15, 9, 0, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "sessions.json")
            session = run_knowledge_lab(
                input_fn=lambda prompt: next(responses),
                output_fn=output.append,
                session_path=path,
                now=now,
            )

            self.assertEqual(session["participant"], "B")
            self.assertEqual(session["score"], 10)
            self.assertTrue(any("Score: 10/10" in line for line in output))
            with open(path, "r", encoding="utf-8") as saved_file:
                self.assertEqual(json.load(saved_file), [session])

    def test_main_menu_exposes_the_knowledge_lab_option(self):
        with patch("builtins.print") as mocked_print:
            from main import display_menu
            display_menu()
        printed_lines = [call.args[0] for call in mocked_print.call_args_list]
        self.assertIn("8. Engineering Knowledge Lab", printed_lines)


if __name__ == "__main__":
    unittest.main()
