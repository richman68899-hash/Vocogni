"""Tests for the shared question-attempt provenance contract."""
import copy
import unittest

import learning_contracts
import question_engine


class QuestionProvenanceContractTests(unittest.TestCase):
    def test_verified_question_metadata_uses_common_versioned_contract(self):
        metadata = question_engine.attempt_metadata(
            "fractions_l1_q1",
            course_id="fractions",
            lesson_id="fractions_l1",
        )

        self.assertEqual(
            metadata["provenance_schema_version"],
            learning_contracts.PROVENANCE_SCHEMA_VERSION,
        )
        self.assertEqual(metadata["question_id"], "fractions_l1_q1")
        self.assertEqual(metadata["course_id"], "fractions")
        self.assertEqual(metadata["lesson_id"], "fractions_l1")
        self.assertEqual(metadata["question_version"], 1)
        self.assertEqual(metadata["skill_id"], "math.number.fraction_representation")
        self.assertEqual(metadata["verification_status"], "verified")
        self.assertEqual(
            learning_contracts.validate_question_provenance(metadata),
            [],
        )

    def test_unregistered_question_remains_legacy_with_context(self):
        metadata = question_engine.attempt_metadata(
            "historical_question",
            course_id="fractions",
            lesson_id="fractions_l3",
        )

        self.assertEqual(metadata["verification_status"], "legacy")
        self.assertEqual(metadata["question_id"], "historical_question")
        self.assertEqual(metadata["course_id"], "fractions")
        self.assertEqual(metadata["lesson_id"], "fractions_l3")
        self.assertEqual(metadata["question_version"], 1)
        self.assertEqual(
            learning_contracts.validate_question_provenance(metadata),
            [],
        )

    def test_optional_context_is_allowed_for_global_question_lookup(self):
        metadata = learning_contracts.build_question_provenance(
            "question-1",
            verification_engine_version="vqe-prototype-1",
        )
        self.assertIsNone(metadata["course_id"])
        self.assertIsNone(metadata["lesson_id"])
        self.assertEqual(
            learning_contracts.validate_question_provenance(metadata),
            [],
        )

    def test_validator_catches_corrupted_provenance_without_reverifying_content(self):
        metadata = learning_contracts.build_question_provenance(
            "question-1",
            course_id="fractions",
            lesson_id="fractions_l1",
            verification_engine_version="vqe-prototype-1",
        )
        corrupted = copy.deepcopy(metadata)
        corrupted["provenance_schema_version"] = 2
        corrupted["question_version"] = 0
        corrupted["verification_status"] = "approved-by-ai"
        corrupted["question_id"] = "  "

        issues = learning_contracts.validate_question_provenance(corrupted)
        self.assertTrue(any("provenance_schema_version" in issue for issue in issues))
        self.assertTrue(any("question_version" in issue for issue in issues))
        self.assertTrue(any("verification_status" in issue for issue in issues))
        self.assertTrue(any("question_id" in issue for issue in issues))

    def test_invalid_values_do_not_silently_become_verified(self):
        metadata = learning_contracts.build_question_provenance(
            "question-1",
            verification_status="unreviewed-but-good",
        )
        self.assertEqual(metadata["verification_status"], "unreviewed-but-good")
        self.assertTrue(
            any(
                "verification_status" in issue
                for issue in learning_contracts.validate_question_provenance(metadata)
            )
        )

    def test_legacy_attempts_without_contract_fields_remain_readable_by_mastery_receipt(self):
        # Historical results predate provenance versioning. They remain valid
        # inputs to the existing receipt builder and are not force-migrated.
        import logic

        progress = {
            "fractions": logic.blank_course_progress(),
        }
        progress["fractions"]["practice_attempts"] = {
            "fractions_l1": [{
                "attempt_number": 1,
                "completed_at": "2026-10-25T05:00:00+00:00",
                "results": [{
                    "question_id": "fractions_l1_q1",
                    "correct": True,
                }],
            }]
        }
        receipt = logic.mastery_receipt_for_course(progress, "fractions")
        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["skills"])


if __name__ == "__main__":
    unittest.main()
