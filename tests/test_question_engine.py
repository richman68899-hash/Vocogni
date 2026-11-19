"""Tests for VQE question schema, review integrity, and strict selection."""
import copy
import unittest
from unittest.mock import patch

import data
import math_taxonomy
import question_engine


class VerifiedQuestionEngineTests(unittest.TestCase):
    def test_taxonomy_prerequisites_resolve_to_known_skills(self):
        for skill_id, skill in math_taxonomy.SKILLS.items():
            with self.subTest(skill_id=skill_id):
                self.assertTrue(skill["label"])
                self.assertTrue(skill["grade_bands"])
                for prerequisite in skill["prerequisites"]:
                    self.assertIn(prerequisite, math_taxonomy.SKILLS)

    def test_registry_is_well_formed_and_seed_items_are_verified(self):
        self.assertEqual(question_engine.validate_registry(), [])
        self.assertGreaterEqual(len(question_engine.VERIFICATION_REGISTRY), 20)

        missing = []
        unverified = []
        for question_id in question_engine.VERIFICATION_REGISTRY:
            record = question_engine.get_question_record(question_id)
            if record is None:
                missing.append(question_id)
            elif record["verification_status"] != "verified":
                unverified.append((question_id, record["verification_status"], record["verification_issues"]))
        self.assertEqual(missing, [])
        self.assertEqual(unverified, [])

    def test_reviewed_snapshot_change_invalidates_question(self):
        record = question_engine.get_question_record(
            "fractions_l1_q1", course_id="fractions", lesson_id="fractions_l1"
        )
        self.assertIsNotNone(record)
        mutated = copy.deepcopy(record)
        mutated["question"]["prompt"] += " (changed)"
        status, issues = question_engine._verification_status(mutated)
        self.assertEqual(status, "needs_review")
        self.assertTrue(any("reviewed snapshot" in issue for issue in issues))

    def test_reviewed_classification_metadata_change_invalidates_question(self):
        original = question_engine.get_review_record("fractions_l1_q1")
        self.assertIsNotNone(original)
        mutated = copy.deepcopy(original)
        mutated["purpose"] = "application"

        with patch.dict(question_engine.VERIFICATION_REGISTRY, {"fractions_l1_q1": mutated}):
            record = question_engine.get_question_record(
                "fractions_l1_q1", course_id="fractions", lesson_id="fractions_l1"
            )
            status, issues = question_engine._verification_status(record)

        self.assertEqual(status, "needs_review")
        self.assertTrue(any("classification metadata" in issue for issue in issues))

    def test_registry_validation_rejects_stale_classification_snapshot(self):
        original = question_engine.get_review_record("fractions_l1_q1")
        mutated = copy.deepcopy(original)
        mutated["grade_bands"] = [9]

        with patch.dict(question_engine.VERIFICATION_REGISTRY, {"fractions_l1_q1": mutated}):
            errors = question_engine.validate_registry()

        self.assertTrue(any("reviewed classification metadata snapshot" in error for error in errors))

    def test_malformed_review_metadata_fails_closed_without_crashing(self):
        original = question_engine.get_review_record("fractions_l1_q1")
        malformed = copy.deepcopy(original)
        malformed["review_checks"] = None
        malformed["grade_bands"] = [{}]
        malformed["skill_id"] = ["not-a-skill"]
        malformed["verification_status"] = "retired"

        with patch.dict(
            question_engine.VERIFICATION_REGISTRY,
            {"fractions_l1_q1": malformed},
        ):
            record = question_engine.get_question_record(
                "fractions_l1_q1",
                course_id="fractions",
                lesson_id="fractions_l1",
            )
            errors = question_engine.validate_registry()

        self.assertIsNotNone(record)
        self.assertEqual(record["verification_status"], "needs_review")
        self.assertTrue(any("Review checks must be a list" in item for item in record["verification_issues"]))
        self.assertTrue(any("Grade 3–9" in item for item in record["verification_issues"]))
        self.assertTrue(any("Unknown VQE skill_id" in item for item in record["verification_issues"]))
        self.assertTrue(any("not marked verified" in item for item in record["verification_issues"]))
        self.assertTrue(errors)

    def test_review_registry_rejects_boolean_difficulty_and_version(self):
        original = question_engine.get_review_record("fractions_l1_q1")
        malformed = copy.deepcopy(original)
        malformed["difficulty"] = True
        malformed["version"] = True

        with patch.dict(
            question_engine.VERIFICATION_REGISTRY,
            {"fractions_l1_q1": malformed},
        ):
            errors = question_engine.validate_registry()
            record = question_engine.get_question_record(
                "fractions_l1_q1",
                course_id="fractions",
                lesson_id="fractions_l1",
            )

        self.assertTrue(any("difficulty must be 1, 2, or 3" in item for item in errors))
        self.assertTrue(any("version must be a positive integer" in item for item in errors))
        self.assertEqual(record["verification_status"], "needs_review")

    def test_shared_validator_rejects_ambiguous_or_malformed_questions(self):
        invalid_mc = {
            "id": "invalid_mc",
            "type": "mc",
            "prompt": "Choose an answer.",
            "options": ["A", "A"],
            "answer": "B",
            "explanation": "A demonstration.",
        }
        errors = question_engine.validate_question(invalid_mc)
        self.assertTrue(any("unique" in issue for issue in errors))
        self.assertTrue(any("match one option" in issue for issue in errors))

        invalid_numeric = {
            "id": "invalid_numeric",
            "type": "numeric",
            "prompt": "Calculate the value.",
            "answer": float("nan"),
            "tolerance": -1,
            "whole_number": "yes",
            "explanation": "A demonstration.",
        }
        errors = question_engine.validate_question(invalid_numeric)
        self.assertTrue(any("finite number" in issue for issue in errors))
        self.assertTrue(any("non-negative" in issue for issue in errors))
        self.assertTrue(any("boolean" in issue for issue in errors))

    def test_verified_only_selection_is_strict_and_deduplicated(self):
        records = question_engine.select_questions(
            course_id="fractions",
            lesson_id="fractions_l1",
            verified_only=True,
            pathway="standard",
        )
        ids = [record["question_id"] for record in records]
        self.assertEqual(ids, [
            "fractions_l1_q1",
            "fractions_l1_q2",
            "fractions_l1_screen3",
        ])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(record["verification_status"] == "verified" for record in records))

    def test_pathway_selection_adds_only_matching_verified_pathway_items(self):
        records = question_engine.select_questions(
            course_id="fractions",
            lesson_id="fractions_l1",
            verified_only=True,
            pathway="level_2",
        )
        ids = {record["question_id"] for record in records}
        self.assertEqual(
            ids,
            {"fractions_l1_q1", "fractions_l1_q2", "fractions_l1_screen3", "fractions_l1_l2_q1"},
        )
        self.assertNotIn("fractions_l1_l3_q2", ids)
        self.assertNotIn("fractions_l1_project_q1", ids)

    def test_pilot_lesson_never_falls_back_to_legacy_content(self):
        # The lesson contains legacy diagnostic content in addition to the
        # curated bank. Strict selection should only return the reviewed set.
        records = question_engine.get_questions(
            course_id="fractions",
            lesson_id="fractions_l1",
            verified_only=False,
            include_pathways=True,
        )
        self.assertTrue(records)
        self.assertTrue(all(item["verification_status"] == "verified" for item in records))
        self.assertFalse(any(item["question_id"] == "fractions_l1_d1" for item in records))

    def test_selection_filters_by_skill_grade_purpose_and_difficulty(self):
        records = question_engine.select_questions(
            skill_id="math.geometry.angle_facts",
            grade_band=7,
            purpose="practice",
            difficulty=1,
            verified_only=True,
        )
        self.assertTrue(records)
        for item in records:
            self.assertEqual(item["question"]["skill_id"], "math.geometry.angle_facts")
            self.assertIn(7, item["question"]["grade_bands"])
            self.assertEqual(item["question"]["purpose"], "practice")
            self.assertEqual(item["question"]["difficulty"], 1)

    def test_normalisation_does_not_mutate_authored_content(self):
        lesson = data.get_course("fractions")["lessons"][0]
        original = copy.deepcopy(lesson["questions"][0])
        record = question_engine.get_question_record(
            "fractions_l1_q1", course_id="fractions", lesson_id="fractions_l1"
        )
        record["question"]["prompt"] = "changed in returned result"
        self.assertEqual(lesson["questions"][0], original)

    def test_question_audit_warns_when_distinct_ids_share_normalised_prompt(self):
        def record(question_id, prompt, question_type="mc"):
            question = {
                "id": question_id,
                "type": question_type,
                "prompt": prompt,
                "options": ["A", "B"],
                "answer": "A",
                "explanation": "A checked explanation.",
            }
            return {
                "question_id": question_id,
                "course_id": "test_course",
                "lesson_id": "test_lesson",
                "source_field": "questions",
                "question": question,
            }

        records = [
            record("q1", "Choose the ＦRACTION that equals 1/2."),
            record("q2", "  choose the FRACTION that equals 1/2.  "),
        ]
        with patch.object(
            question_engine,
            "_catalogue",
            return_value=(records, [], len(records)),
        ):
            report = question_engine.audit_question_bank()

        duplicate_issues = [
            issue for issue in report["issues"]
            if issue.get("code") == "duplicate_prompt"
        ]
        self.assertEqual(report["duplicate_prompt_group_count"], 1)
        self.assertEqual(len(duplicate_issues), 1)
        self.assertEqual(duplicate_issues[0]["question_ids"], ["q1", "q2"])
        self.assertEqual(duplicate_issues[0]["severity"], "warning")
        self.assertEqual(len(duplicate_issues[0]["locations"]), 2)

    def test_question_audit_does_not_flag_same_id_or_different_types_as_prompt_duplicates(self):
        def record(question_id, prompt, question_type):
            question = {
                "id": question_id,
                "type": question_type,
                "prompt": prompt,
                "options": ["A", "B"] if question_type == "mc" else None,
                "answer": "A" if question_type == "mc" else 1,
                "explanation": "A checked explanation.",
            }
            return {
                "question_id": question_id,
                "course_id": "test_course",
                "lesson_id": "test_lesson",
                "source_field": "questions",
                "question": question,
            }

        records = [
            record("same-id", "What is 2 + 2?", "mc"),
            record("same-id", "What is 2 + 2?", "mc"),
            record("different-type", "What is 2 + 2?", "numeric"),
            record("different-prompt", "What is 3 + 3?", "mc"),
        ]
        with patch.object(
            question_engine,
            "_catalogue",
            return_value=(records, [], len(records)),
        ):
            report = question_engine.audit_question_bank()

        self.assertEqual(report["duplicate_prompt_group_count"], 0)
        self.assertFalse(
            any(issue.get("code") == "duplicate_prompt" for issue in report["issues"])
        )

    def test_bank_audit_distinguishes_verified_items_from_legacy_content(self):
        report = question_engine.audit_question_bank(course_id="fractions")
        self.assertGreaterEqual(report["verified_count"], 6)
        self.assertGreater(report["legacy_count"], 0)
        self.assertEqual(report["needs_review_count"], 0)
        self.assertEqual(report["counts"]["verified"], report["verified_count"])

    def test_malformed_unreviewed_question_remains_needs_review_after_normalisation(self):
        course_id = "vqe_invalid_legacy_test"
        question = {
            "id": "invalid_legacy_q",
            "type": "mc",
            "prompt": "Choose the answer.",
            "options": ["A", "A"],
            "answer": "B",
            "explanation": "This item is deliberately invalid for the test.",
            "mistake_tag": "test",
        }
        test_course = {
            "id": course_id,
            "title": "Invalid legacy test",
            "topic_label": "Invalid legacy test",
            "short_description": "Test-only data.",
            "lessons": [{
                "id": "lesson_1",
                "title": "Invalid lesson",
                "questions": [question],
            }],
        }
        with patch.dict(data.COURSES, {course_id: test_course}), patch.object(
            data, "COURSE_ORDER", list(data.COURSE_ORDER) + [course_id]
        ):
            records = question_engine.iter_question_records(course_id=course_id)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["verification_status"], "needs_review")
        self.assertTrue(records[0]["verification_issues"])

    def test_conflicting_duplicate_ids_are_excluded_from_vqe(self):
        q1 = {
            "id": "duplicate_test_q",
            "type": "mc",
            "prompt": "Pick one.",
            "options": ["A", "B"],
            "answer": "A",
            "explanation": "A is the answer.",
            "mistake_tag": "Test",
        }
        q2 = dict(q1, prompt="Pick a different one.")
        course_id = "vqe_duplicate_test"
        test_course = {
            "id": course_id,
            "title": "VQE duplicate test",
            "topic_label": "VQE duplicate test",
            "short_description": "Test-only data.",
            "lessons": [
                {"id": "one", "title": "One", "questions": [q1]},
                {"id": "two", "title": "Two", "questions": [q2]},
            ],
        }
        with patch.dict(data.COURSES, {course_id: test_course}), patch.object(
            data, "COURSE_ORDER", list(data.COURSE_ORDER) + [course_id]
        ):
            report = question_engine.audit_question_bank(course_id=course_id)
            self.assertTrue(any(
                item.get("code") == "duplicate_global_id"
                for item in report["issues"]
            ))
            records = question_engine.select_questions(
                course_id=course_id, verified_only=True
            )
            self.assertEqual(records, [])

            # A lesson-scoped lookup must still notice the duplicate ID in
            # the other lesson; filtering must not turn it back into "verified".
            scoped = question_engine.iter_question_records(
                course_id=course_id, lesson_id="one"
            )
            self.assertEqual(len(scoped), 1)
            self.assertEqual(scoped[0]["verification_status"], "needs_review")
            self.assertTrue(any(
                "conflicting authored content" in issue
                for issue in scoped[0]["verification_issues"]
            ))



    def test_difficulty_preference_softly_orders_without_filtering(self):
        questions = [
            {"id": "medium", "difficulty": 2},
            {"id": "easy", "difficulty": 1},
            {"id": "hard", "difficulty": 3},
            {"id": "unknown"},
        ]
        self.assertEqual(
            [item["id"] for item in question_engine.order_questions_for_preference(questions, "Easy")],
            ["easy", "medium", "hard", "unknown"],
        )
        self.assertEqual(
            [item["id"] for item in question_engine.order_questions_for_preference(questions, "Hard")],
            ["hard", "medium", "easy", "unknown"],
        )
        self.assertEqual(
            [item["id"] for item in question_engine.order_questions_for_preference(questions, "Medium")],
            ["medium", "easy", "hard", "unknown"],
        )
        self.assertEqual(
            question_engine.order_questions_for_preference(questions, "Adaptive"),
            questions,
        )
        self.assertEqual(len(question_engine.order_questions_for_preference(questions, "Hard")), 4)

    def test_review_registry_records_explicit_provenance_and_scope(self):
        metadata = question_engine.get_review_record("fractions_l1_q1")
        self.assertEqual(metadata["reviewer_kind"], "internal_team")
        self.assertEqual(metadata["review_evidence_type"], "seed_content_review")
        self.assertEqual(metadata["review_independence"], "not_independently_audited")
        self.assertIn("expected_answer", metadata["review_scope"])
        self.assertEqual(question_engine.validate_registry(), [])

    def test_registry_rejects_missing_review_provenance(self):
        metadata = question_engine.get_review_record("fractions_l1_q1")
        metadata.pop("reviewer_kind")
        with patch.dict(question_engine.VERIFICATION_REGISTRY, {
            "fractions_l1_q1": metadata,
        }):
            record = question_engine.get_question_record(
                "fractions_l1_q1", course_id="fractions", lesson_id="fractions_l1"
            )
            self.assertEqual(record["verification_status"], "needs_review")
            self.assertTrue(any("reviewer kind" in issue for issue in record["verification_issues"]))

    def test_registry_rejects_non_string_review_scope_without_crashing(self):
        metadata = question_engine.get_review_record("fractions_l1_q1")
        metadata["review_scope"] = [{}]
        with patch.dict(question_engine.VERIFICATION_REGISTRY, {
            "fractions_l1_q1": metadata,
        }):
            record = question_engine.get_question_record(
                "fractions_l1_q1", course_id="fractions", lesson_id="fractions_l1"
            )
        self.assertEqual(record["verification_status"], "needs_review")
        self.assertTrue(any("review scope" in issue for issue in record["verification_issues"]))

    def test_bank_audit_reports_per_lesson_coverage_and_review_limits(self):
        report = question_engine.audit_question_bank(course_id="fractions")
        self.assertTrue(report["lesson_coverage"])
        first = report["lesson_coverage"][0]
        self.assertIn("verified_percent", first)
        self.assertGreaterEqual(first["total"], first["counts"]["verified"])
        self.assertEqual(
            report["review_provenance"]["verified_by_independence"],
            {"not_independently_audited": report["verified_count"]},
        )
        self.assertTrue(report["review_provenance"]["limitations"])

if __name__ == "__main__":
    unittest.main()
