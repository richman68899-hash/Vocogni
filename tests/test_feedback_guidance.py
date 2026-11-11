"""Tests for deterministic, non-diagnostic answer feedback guidance."""
import unittest

import feedback_guidance


class FeedbackGuidanceTests(unittest.TestCase):
    def test_known_mistake_tag_returns_explanation_and_next_step(self):
        guidance = feedback_guidance.build_feedback_guidance({
            "mistake_tag": "Denominator confusion",
        })
        self.assertIsNotNone(guidance)
        self.assertIn("denominator", guidance["likely_issue"].lower())
        self.assertTrue(guidance["next_step"])
        self.assertEqual(guidance["source_tag"], "Denominator confusion")

    def test_tag_matching_is_case_and_whitespace_insensitive(self):
        guidance = feedback_guidance.build_feedback_guidance({
            "mistake_tag": "  SIGN   ERRORS ",
        })
        self.assertIsNotNone(guidance)
        self.assertIn("negative sign", guidance["likely_issue"].lower())

    def test_known_tag_includes_a_tag_specific_worked_example(self):
        guidance = feedback_guidance.build_feedback_guidance({
            "mistake_tag": "Denominator confusion",
        })
        self.assertIn("3 of 5", guidance["worked_example"])
        self.assertIn("denominator", guidance["worked_example"].lower())

    def test_tag_without_authored_example_returns_empty_example(self):
        guidance = feedback_guidance.build_feedback_guidance({
            "mistake_tag": "selecting relevant information",
        })
        self.assertIsNotNone(guidance)
        self.assertEqual(guidance["worked_example"], "")

    def test_unknown_tag_is_not_mislabelled(self):
        self.assertIsNone(feedback_guidance.build_feedback_guidance({
            "mistake_tag": "Unreviewed misconception",
        }))

    def test_missing_or_invalid_question_returns_no_guidance(self):
        self.assertIsNone(feedback_guidance.build_feedback_guidance(None))
        self.assertIsNone(feedback_guidance.build_feedback_guidance({}))
        self.assertIsNone(feedback_guidance.build_feedback_guidance({
            "mistake_tag": "   ",
        }))


    def test_verified_question_gets_exact_distractor_explanation(self):
        question = {
            "id": "fractions_l1_q1",
            "type": "mc",
            "verification_status": "verified",
            "options": ["3/4", "4/3", "1/3", "3/3"],
            "answer": "3/4",
        }
        feedback = feedback_guidance.build_distractor_feedback(question, "4/3")
        self.assertIsNotNone(feedback)
        self.assertIn("reverses", feedback["explanation"])
        self.assertEqual(feedback["selected_option"], "4/3")
        self.assertEqual(feedback["source"], "authored_distractor")

    def test_distractor_matching_is_exact_and_rejects_unmapped_options(self):
        question = {
            "id": "fractions_l1_q1",
            "type": "mc",
            "verification_status": "verified",
            "options": ["3/4", "4/3", "1/3", "3/3"],
            "answer": "3/4",
        }
        self.assertIsNone(feedback_guidance.build_distractor_feedback(question, "4 / 3"))
        self.assertIsNone(feedback_guidance.build_distractor_feedback(question, "unknown"))

    def test_distractor_feedback_requires_verified_mc_question_and_wrong_answer(self):
        question = {
            "id": "fractions_l1_q1",
            "type": "mc",
            "verification_status": "legacy",
            "options": ["3/4", "4/3", "1/3", "3/3"],
            "answer": "3/4",
        }
        self.assertIsNone(feedback_guidance.build_distractor_feedback(question, "4/3"))
        question["verification_status"] = "verified"
        self.assertIsNone(feedback_guidance.build_distractor_feedback(question, "3/4"))
        question["type"] = "numeric"
        self.assertIsNone(feedback_guidance.build_distractor_feedback(question, "4/3"))

if __name__ == "__main__":
    unittest.main()
