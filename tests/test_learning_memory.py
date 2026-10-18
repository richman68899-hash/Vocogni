import unittest

import learning_memory


class LearningMemoryTests(unittest.TestCase):
    def setUp(self):
        self.progress = {}
        self.question = {
            "id": "q1", "type": "open_ended",
            "skill_tag": "Quadratic inequalities",
            "mistake_tag": "Endpoint inclusion",
        }
        self.marking = {
            "score": 1, "max_marks": 2, "full_credit": False,
            "marking_points": [
                {"id": "roots", "criteria": "Finds both roots", "marks_awarded": 1, "marks_available": 1, "met": True},
                {"id": "endpoints", "criteria": "Includes endpoints for an inclusive inequality", "marks_awarded": 0, "marks_available": 1, "met": False},
            ],
        }

    def record(self, qid="q1", marking=None, skill=None):
        question = dict(self.question, id=qid)
        if skill:
            question["skill_tag"] = skill
        return learning_memory.record_attempt(
            self.progress, "maths", "lesson_1", "Quadratic inequalities",
            question, False, marking or self.marking, source="practice",
        )

    def test_records_score_and_rubric_evidence_without_raw_answer(self):
        self.record()
        memory = self.progress["maths"]["learning_memory"]
        skill = memory["skills"]["quadratic_inequalities"]
        self.assertEqual((skill["attempts"], skill["marks_awarded"], skill["max_marks"]), (1, 1, 2))
        self.assertEqual(skill["criterion_history"]["endpoints"]["misses"], 1)
        self.assertNotIn("user_answer", skill["evidence"][0])
        self.assertNotIn("prompt", skill["evidence"][0])
        self.assertEqual(memory["attempts_recorded"], 1)

    def test_repeat_snag_only_appears_after_two_misses(self):
        self.record("q1")
        self.assertEqual(learning_memory.course_fingerprint(self.progress, "maths")["repeat_snags"], [])
        self.record("q2")
        repeated = learning_memory.course_fingerprint(self.progress, "maths")["repeat_snags"]
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["id"], "endpoints")
        self.assertEqual(repeated[0]["misses"], 2)

    def test_feedback_nudge_targets_currently_missed_repeat_criterion(self):
        self.record()
        self.record("q2")
        nudge = learning_memory.feedback_nudge(self.progress, "maths", self.question, self.marking)
        self.assertIsNotNone(nudge)
        self.assertIn("endpoints", nudge["criterion"].casefold())
        self.assertIn("roots", nudge["repair"].casefold())
        already_fixed = {"marking_points": [{"id": "endpoints", "met": True}]}
        self.assertIsNone(learning_memory.feedback_nudge(self.progress, "maths", self.question, already_fixed))
        self.assertIsNone(learning_memory.feedback_nudge(self.progress, "maths", dict(self.question, skill_tag="Factoring"), self.marking))

    def test_consistent_evidence_requires_three_recent_strong_attempts(self):
        question = {"id": "q", "skill_tag": "Factoring", "mistake_tag": "Factoring"}
        for _ in range(3):
            learning_memory.record_attempt(self.progress, "maths", "lesson_1", "Factoring",
                question, True, {"score": 4, "max_marks": 4, "marking_points": []})
        profile = learning_memory.course_fingerprint(self.progress, "maths")
        self.assertEqual(profile["skills"][0]["status"], "Consistent evidence")
        self.assertEqual(profile["reliable_count"], 1)

    def test_legacy_progress_is_preserved_and_missing_metadata_falls_back(self):
        self.progress = {"maths": {"questions_attempted": 7, "mistakes": {"old": 2}}}
        learning_memory.record_attempt(self.progress, "maths", "lesson_2", "Legacy lesson",
            {"id": "old_q", "mistake_tag": "Old skill"}, False)
        self.assertEqual(self.progress["maths"]["questions_attempted"], 7)
        self.assertEqual(self.progress["maths"]["mistakes"], {"old": 2})
        self.assertIn("old_skill", self.progress["maths"]["learning_memory"]["skills"])

    def test_repair_rules_are_deterministic(self):
        self.assertIn("roots", learning_memory.repair_suggestion("Quadratic inequalities", "Endpoint inclusion").casefold())
        self.assertIn("equate", learning_memory.repair_suggestion("Simultaneous equations").casefold())
        self.assertIn("b²", learning_memory.repair_suggestion("Discriminant"))


if __name__ == "__main__":
    unittest.main()
