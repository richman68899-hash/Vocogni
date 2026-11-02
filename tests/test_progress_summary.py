"""Tests for the deterministic AI progress summary and its preference handling."""

import unittest

import data
import logic


def sample_progress():
    weakest_id, strongest_id = data.COURSE_ORDER[:2]
    return {
        weakest_id: {
            "started": True,
            "questions_attempted": 10,
            "correct_answers": 4,
            "mistakes": {
                "sign_error": 3,
                "calculation_error": 2,
            },
            "completed_lessons": [],
        },
        strongest_id: {
            "started": True,
            "questions_attempted": 10,
            "correct_answers": 9,
            "mistakes": {},
            "completed_lessons": [],
        },
    }


class ProgressSummaryPreferenceTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "name": "Test Learner",
            "preferred_language": "English",
        }
        self.progress = sample_progress()

    def summary(self, **preferences):
        return logic.generate_progress_summary(
            self.profile,
            self.progress,
            preferences=preferences,
        )

    def test_response_language_uses_selected_language(self):
        english = self.summary(ai_preview_response_language="English")
        indonesian = self.summary(ai_preview_response_language="Bahasa Indonesia")
        mandarin = self.summary(ai_preview_response_language="Mandarin")

        self.assertIn("Here is your current learning snapshot", english)
        self.assertIn("Berikut gambaran kemajuan", indonesian)
        self.assertIn("以下是你目前的学习情况", mandarin)

    def test_match_lesson_language_uses_profile_language(self):
        profile = dict(self.profile, preferred_language="Bahasa Indonesia")
        result = logic.generate_progress_summary(
            profile,
            self.progress,
            preferences={"ai_preview_response_language": "Match lesson language"},
        )
        self.assertIn("Berikut gambaran kemajuan", result)

    def test_teaching_style_and_follow_up_change_summary(self):
        socratic = self.summary(
            ai_preview_teaching_style="Socratic (ask me questions)",
            ai_preview_follow_up_questions=True,
        )
        direct = self.summary(
            ai_preview_teaching_style="Direct and concise",
            ai_preview_follow_up_questions=True,
        )

        self.assertIn("Understanding check", socratic)
        self.assertIn("Priority:", direct)
        self.assertNotEqual(socratic, direct)

    def test_explanation_depth_changes_evidence_detail(self):
        balanced = self.summary(ai_preview_explanation_depth="Balanced")
        detailed = self.summary(ai_preview_explanation_depth="In-depth")

        self.assertNotIn("Course-by-course recorded performance", balanced)
        self.assertIn("Course-by-course recorded performance", detailed)
        self.assertIn("Interpretation:", detailed)

    def test_challenge_and_adaptive_mastery_change_guidance(self):
        confidence = self.summary(
            ai_preview_challenge_level="Build confidence",
            ai_preview_adaptive_mastery=False,
        )
        stretch = self.summary(
            ai_preview_challenge_level="Stretch me",
            ai_preview_adaptive_mastery=True,
        )

        self.assertIn("steady sequence", confidence)
        self.assertIn("consolidate", confidence)
        self.assertIn("more demanding application", stretch)
        self.assertNotEqual(confidence, stretch)

    def test_hint_and_correction_preferences_change_instructions(self):
        progressive = self.summary(
            ai_preview_hint_strategy="Progressive hints",
            ai_preview_correction_style="Show the corrected method",
        )
        guided = self.summary(
            ai_preview_hint_strategy="Guided questions",
            ai_preview_correction_style="Ask me to find the error",
        )

        self.assertIn("one small clue at a time", progressive)
        self.assertIn("reconstruct the solution", progressive)
        self.assertIn("what is known", guided)
        self.assertIn("first step", guided)

    def test_lesson_scope_suppresses_cross_topic_transfer(self):
        scoped = self.summary(
            ai_preview_lesson_scope=True,
            ai_preview_transfer_questions=True,
            ai_preview_everyday_examples=True,
        )
        broad = self.summary(
            ai_preview_lesson_scope=False,
            ai_preview_transfer_questions=True,
            ai_preview_everyday_examples=True,
        )

        self.assertIn("Keep this next action within", scoped)
        self.assertNotIn("Transfer:", scoped)
        self.assertNotIn("familiar real-world situation", scoped)
        self.assertIn("Transfer:", broad)
        self.assertIn("familiar real-world situation", broad)

    def test_evidence_and_uncertainty_toggles_are_respected(self):
        detailed = self.summary(
            ai_preview_show_sources=True,
            ai_preview_flag_uncertainty=True,
        )
        minimal = self.summary(
            ai_preview_show_sources=False,
            ai_preview_flag_uncertainty=False,
        )

        self.assertIn("Evidence used:", detailed)
        self.assertIn("Evidence limits:", detailed)
        self.assertNotIn("Evidence used:", minimal)
        self.assertIn("not a definitive mastery assessment", minimal)

    def test_context_permission_controls_display_name(self):
        personalized = self.summary(ai_preview_context_permission=True)
        private = self.summary(ai_preview_context_permission=False)

        self.assertIn("Hi Test Learner", personalized)
        self.assertNotIn("Test Learner", private)
        self.assertIn("Your display name was not used", private)

    def test_memory_review_exposes_applied_preferences(self):
        reviewed = self.summary(
            ai_preview_memory_review=True,
            ai_preview_teaching_style="Detailed instructor",
        )
        hidden = self.summary(ai_preview_memory_review=False)

        self.assertIn("Settings applied:", reviewed)
        self.assertIn("Teaching approach: Detailed instructor", reviewed)
        self.assertNotIn("Settings applied:", hidden)

    def test_local_capability_limits_are_never_misrepresented(self):
        result = self.summary(
            ai_preview_model_preference="Advanced reasoning",
            ai_preview_speed_preference="Prioritize depth",
            ai_preview_web_research=True,
            ai_preview_image_input=True,
        )
        self.assertIn("not active in this offline summary", result)
        self.assertIn("No external sources are consulted", result)

    def test_exam_and_bullet_formats_are_applied(self):
        exam = self.summary(ai_preview_answer_format="Exam-style response")
        bullets = self.summary(ai_preview_answer_format="Bullet points")

        self.assertTrue(exam.startswith("Vocogni Learning Summary"))
        self.assertIn("Performance overview", exam)
        self.assertIn("- Hi Test Learner", bullets)

    def test_summary_signature_changes_with_settings_and_progress(self):
        base = logic.progress_summary_signature(
            self.profile, self.progress, {"ai_preview_challenge_level": "Adaptive"}
        )
        changed_settings = logic.progress_summary_signature(
            self.profile, self.progress, {"ai_preview_challenge_level": "Stretch me"}
        )
        changed_progress = sample_progress()
        changed_progress[data.COURSE_ORDER[0]]["correct_answers"] = 5
        changed_data = logic.progress_summary_signature(
            self.profile, changed_progress, {"ai_preview_challenge_level": "Adaptive"}
        )

        self.assertEqual(
            base,
            logic.progress_summary_signature(
                self.profile, self.progress, {"ai_preview_challenge_level": "Adaptive"}
            ),
        )
        self.assertNotEqual(base, changed_settings)
        self.assertNotEqual(base, changed_data)


if __name__ == "__main__":
    unittest.main()
