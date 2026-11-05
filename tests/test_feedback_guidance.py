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


if __name__ == "__main__":
    unittest.main()
