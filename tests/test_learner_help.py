"""Tests for the verified-question progressive help ladder."""
import unittest

import learner_help


class LearnerHelpTests(unittest.TestCase):
    def test_verified_question_reveals_authored_steps_in_order(self):
        question = {
            "id": "fraction_q1",
            "mistake_tag": "Denominator confusion",
            "input_hint": "Count the equal parts before writing the fraction.",
            "answer": "7/8",
            "explanation": "This is the exact solution and must not be reused as a hint.",
        }
        lesson = {
            "title": "Fractions",
            "explanation": "A denominator counts the equal parts in one whole.",
            "worked_example": "If 3 of 5 equal parts are selected, the fraction is 3/5.",
        }

        ladder = learner_help.build_help_ladder(
            question, lesson, verification_status="verified"
        )

        self.assertTrue(ladder["available"])
        self.assertEqual(ladder["focus"], "Denominator confusion")
        self.assertEqual(
            [step["label"] for step in ladder["steps"]],
            ["First cue", "Key idea", "Try this next", "Similar worked example"],
        )
        self.assertEqual(
            ladder["steps"][0]["content"],
            "Count the equal parts before writing the fraction.",
        )
        all_help = " ".join(step["content"] for step in ladder["steps"])
        self.assertNotIn(question["explanation"], all_help)
        self.assertNotIn("7/8", all_help)

    def test_unknown_tag_falls_back_to_existing_lesson_material(self):
        ladder = learner_help.build_help_ladder(
            {"mistake_tag": "Unreviewed tag"},
            {
                "title": "Algebra",
                "explanation": "A variable represents a number.",
                "worked_example": "If x = 4, then 2x = 8.",
            },
            verification_status="verified",
        )
        self.assertTrue(ladder["available"])
        self.assertEqual(
            [step["label"] for step in ladder["steps"]],
            ["Review the core idea", "Compare a worked example"],
        )

    def test_known_tag_without_specific_example_uses_lesson_worked_example(self):
        ladder = learner_help.build_help_ladder(
            {"mistake_tag": "selecting relevant information"},
            {
                "title": "Word problems",
                "explanation": "Identify the quantity the question asks you to find.",
                "worked_example": "List each relevant quantity before choosing an operation.",
            },
            verification_status="verified",
        )
        self.assertTrue(ladder["available"])
        self.assertIn(
            "List each relevant quantity before choosing an operation.",
            [step["content"] for step in ladder["steps"]],
        )

    def test_unverified_questions_never_receive_the_guided_ladder(self):
        for status in ("legacy", "unverified", None, ""):
            with self.subTest(status=status):
                ladder = learner_help.build_help_ladder(
                    {"mistake_tag": "Denominator confusion"},
                    {"title": "Fractions", "explanation": "Core idea", "worked_example": "Example"},
                    verification_status=status,
                )
                self.assertFalse(ladder["available"])
                self.assertEqual(ladder["reason"], "unverified_content")
                self.assertEqual(ladder["steps"], [])

    def test_independent_transfer_questions_remain_hint_free(self):
        ladder = learner_help.build_help_ladder(
            {
                "mistake_tag": "Denominator confusion",
                "_is_transfer_check": True,
            },
            {"title": "Fractions", "explanation": "Core idea", "worked_example": "Example"},
            verification_status="verified",
        )
        self.assertFalse(ladder["available"])
        self.assertEqual(ladder["reason"], "independent_transfer")
        self.assertEqual(ladder["steps"], [])

    def test_no_authored_support_is_reported_instead_of_invented(self):
        ladder = learner_help.build_help_ladder(
            {"id": "unknown_q", "mistake_tag": "Unknown tag"},
            {"title": "Untitled"},
            verification_status="verified",
        )
        self.assertFalse(ladder["available"])
        self.assertEqual(ladder["reason"], "no_authored_support")

    def test_malformed_inputs_fail_closed(self):
        ladder = learner_help.build_help_ladder(
            None, {}, verification_status="verified"
        )
        self.assertFalse(ladder["available"])
        self.assertEqual(ladder["reason"], "invalid_content")


if __name__ == "__main__":
    unittest.main()
