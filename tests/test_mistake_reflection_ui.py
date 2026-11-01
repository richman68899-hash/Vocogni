"""Ensure Mistake Reflection is available across every lesson feedback path."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MistakeReflectionUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")

    def _function_source(self, name, next_marker):
        start = self.source.index(f"def {name}(")
        end = self.source.index(next_marker, start)
        return self.source[start:end]

    def test_shared_immediate_feedback_renders_reflection_for_wrong_answers(self):
        feedback = self._function_source(
            "_render_feedback",
            "# ===========================================================================\n# COMPLETE",
        )
        self.assertIn("if not is_correct:", feedback)
        self.assertIn("_render_mistake_reflection(", feedback)

    def test_every_incorrect_answer_can_reach_feedback_even_when_full_feedback_is_deferred(self):
        self.assertIn(
            "or not is_correct",
            self.source,
        )
        self.assertIn(
            "the full answer explanations will appear in the lesson summary.",
            self.source,
        )

    def test_answer_identity_is_saved_with_structured_lesson_checkpoint_and_result(self):
        self.assertIn('"answer_id": answer_id,', self.source)
        self.assertIn('"question_prompt": str(question.get("prompt") or ""),', self.source)
        self.assertIn('"answer_id": checkpoint.get("answer_id") or uuid4().hex,', self.source)

    def test_reflections_are_saved_as_durable_data_not_notes(self):
        self.assertIn("mistake_reflections.upsert_mistake_reflection(", self.source)
        self.assertIn('course_progress, answer_id', self.source)
        self.assertIn("state.flush_persistent_save()", self.source)
        self.assertNotIn("st.session_state.notes.append", self.source)

    def test_reflection_does_not_change_scoring_or_answer_marking(self):
        self.assertIn('result.get("correct") is not False', self.source)
        self.assertIn('result["mistake_reflection_id"] = record["answer_id"]', self.source)
        self.assertIn("logic.record_answer(", self.source)


if __name__ == "__main__":
    unittest.main()
