import unittest
from unittest.mock import patch

import question_engine
import skill_confirmation


class SkillConfirmationTests(unittest.TestCase):
    def test_selects_a_different_verified_question_for_the_same_skill(self):
        record = skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
            exclude_question_ids={"fractions_l1_q1"},
        )
        self.assertIsNotNone(record)
        self.assertNotEqual(record["question_id"], "fractions_l1_q1")
        self.assertEqual(record["verification_status"], "verified")
        self.assertEqual(record["question"]["skill_id"], "math.number.fraction_representation")
        self.assertIn(record["question"]["type"], {"mc", "numeric"})

    def test_no_candidate_is_returned_when_every_item_is_excluded(self):
        all_ids = {
            record["question_id"]
            for record in question_engine.select_questions(
                course_id="fractions",
                skill_id="math.number.fraction_representation",
                verified_only=True,
                include_pathways=True,
            )
        }
        self.assertIsNone(skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
            exclude_question_ids=all_ids,
        ))

    def test_confirmation_is_saved_separately_without_raw_answer(self):
        record = skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
            exclude_question_ids={"fractions_l1_q1"},
        )
        progress = {}
        result = skill_confirmation.record_confirmation(
            progress, record, record["question"]["answer"]
        )
        self.assertTrue(result["correct"])
        saved = progress["fractions"]["skill_confirmation_attempts"][0]
        self.assertEqual(saved["source"], "diagnostic_confirmation")
        self.assertEqual(saved["results"][0]["verification_status"], "verified")
        self.assertNotIn("user_answer", saved["results"][0])
        self.assertNotIn("question_prompt", saved["results"][0])

    def test_duplicate_question_cannot_be_used_twice(self):
        record = skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
        )
        progress = {}
        skill_confirmation.record_confirmation(
            progress, record, record["question"]["answer"]
        )
        with self.assertRaisesRegex(ValueError, "already been used"):
            skill_confirmation.record_confirmation(
                progress, record, record["question"]["answer"]
            )

    def test_confirmation_rejected_if_question_is_no_longer_verified(self):
        record = skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
        )
        progress = {}
        with patch.object(
            question_engine,
            "attempt_metadata",
            return_value={"verification_status": "needs_review", "skill_id": "math.number.fraction_representation"},
        ):
            with self.assertRaisesRegex(ValueError, "no longer verified"):
                skill_confirmation.record_confirmation(
                    progress, record, record["question"]["answer"]
                )
        self.assertEqual(progress, {})

    def test_invalid_input_does_not_mutate_progress(self):
        record = skill_confirmation.select_confirmation_question(
            course_id="fractions",
            skill_id="math.number.fraction_representation",
        )
        progress = {}
        with self.assertRaisesRegex(ValueError, "answer is required"):
            skill_confirmation.record_confirmation(progress, record, "  ")
        self.assertEqual(progress, {})


if __name__ == "__main__":
    unittest.main()
