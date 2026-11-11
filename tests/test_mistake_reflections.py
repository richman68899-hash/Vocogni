"""Tests for structured, answer-linked learner mistake reflections."""
import unittest

from mistake_reflections import (
    MAX_REFLECTION_LENGTH,
    find_mistake_reflection,
    normalize_reflection_text,
    upsert_mistake_reflection,
)


class MistakeReflectionTests(unittest.TestCase):
    def setUp(self):
        self.course_progress = {}

    def _save(self, text="I used the wrong operation."):
        return upsert_mistake_reflection(
            self.course_progress,
            answer_id="answer-1",
            course_id="chemistry",
            lesson_id="concentration",
            question_id="q-01",
            attempt_number=2,
            question_prompt="Calculate concentration.",
            text=text,
            now="2026-11-01T10:00:00+00:00",
        )

    def test_saves_reflection_as_learner_authored_system_data(self):
        record = self._save()
        self.assertEqual(record["text"], "I used the wrong operation.")
        self.assertEqual(record["source"], "learner")
        self.assertEqual(record["answer_id"], "answer-1")
        self.assertEqual(record["course_id"], "chemistry")
        self.assertEqual(record["lesson_id"], "concentration")
        self.assertEqual(record["question_id"], "q-01")
        self.assertEqual(len(self.course_progress["mistake_reflections"]), 1)

    def test_updates_existing_answer_reflection_without_duplicate(self):
        first = self._save()
        updated = upsert_mistake_reflection(
            self.course_progress,
            answer_id="answer-1",
            course_id="chemistry",
            lesson_id="concentration",
            question_id="q-01",
            attempt_number=2,
            text="I misunderstood what concentration measures.",
            now="2026-11-01T11:00:00+00:00",
        )
        self.assertIs(first, updated)
        self.assertEqual(len(self.course_progress["mistake_reflections"]), 1)
        self.assertEqual(
            find_mistake_reflection(self.course_progress, "answer-1")["text"],
            "I misunderstood what concentration measures.",
        )

    def test_reflections_for_different_answers_remain_separate(self):
        self._save()
        upsert_mistake_reflection(
            self.course_progress,
            answer_id="answer-2",
            course_id="chemistry",
            lesson_id="concentration",
            question_id="q-02",
            attempt_number=2,
            text="I forgot to convert the volume units.",
            now="2026-11-01T10:02:00+00:00",
        )
        self.assertEqual(len(self.course_progress["mistake_reflections"]), 2)
        self.assertIsNone(find_mistake_reflection(self.course_progress, "missing"))

    def test_empty_reflection_is_rejected(self):
        with self.assertRaises(ValueError):
            self._save("   ")

    def test_reflection_length_is_bounded(self):
        value = normalize_reflection_text("x" * (MAX_REFLECTION_LENGTH + 20))
        self.assertEqual(len(value), MAX_REFLECTION_LENGTH)

    def test_answer_evidence_is_not_modified(self):
        self.course_progress.update({
            "questions_attempted": 1,
            "correct_answers": 0,
            "mistakes": {"Other": 1},
        })
        before = {
            "questions_attempted": self.course_progress["questions_attempted"],
            "correct_answers": self.course_progress["correct_answers"],
            "mistakes": dict(self.course_progress["mistakes"]),
        }
        upsert_mistake_reflection(
            self.course_progress,
            answer_id="answer-1",
            course_id="math",
            lesson_id="algebra",
            question_id="q-1",
            attempt_number=1,
            text="I rushed the calculation.",
            now="2026-11-01T10:00:00+00:00",
        )
        self.assertEqual(
            {
                "questions_attempted": self.course_progress["questions_attempted"],
                "correct_answers": self.course_progress["correct_answers"],
                "mistakes": self.course_progress["mistakes"],
            },
            before,
        )


if __name__ == "__main__":
    unittest.main()
