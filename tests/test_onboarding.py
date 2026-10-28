"""Regression tests for the first-run guided tutorial."""
import unittest

from onboarding import (
    TUTORIAL_STEPS,
    get_tutorial_step,
    is_tutorial_complete,
    normalize_step_index,
)


class OnboardingTests(unittest.TestCase):
    def test_old_and_new_settings_default_to_showing_tour(self):
        self.assertFalse(is_tutorial_complete({}))
        self.assertFalse(is_tutorial_complete(None))
        self.assertFalse(is_tutorial_complete({"tutorial_completed": False}))
        self.assertTrue(is_tutorial_complete({"tutorial_completed": True}))

    def test_only_explicit_boolean_true_marks_tutorial_complete(self):
        self.assertFalse(is_tutorial_complete({"tutorial_completed": "true"}))
        self.assertFalse(is_tutorial_complete({"tutorial_completed": 1}))

    def test_tutorial_covers_core_app_areas_and_replay(self):
        routes = {step["route"] for step in TUTORIAL_STEPS}
        titles = {step["short_title"] for step in TUTORIAL_STEPS}
        self.assertTrue({"Browse", "Progress", "Notes", "Profile", "Settings"} <= routes)
        self.assertTrue({"Learn", "Practice", "Progress", "Notes", "Profile", "Assistant", "Settings"} <= titles)
        self.assertIn("replay", TUTORIAL_STEPS[-1]["detail"].lower())

    def test_step_normalization_handles_bad_and_out_of_range_values(self):
        self.assertEqual(normalize_step_index(None), 0)
        self.assertEqual(normalize_step_index("bad"), 0)
        self.assertEqual(normalize_step_index(True), 0)
        self.assertEqual(normalize_step_index(-4), 0)
        self.assertEqual(normalize_step_index(999), len(TUTORIAL_STEPS) - 1)
        self.assertEqual(get_tutorial_step(999), TUTORIAL_STEPS[-1])

    def test_all_steps_have_content_and_valid_routes(self):
        valid_routes = {"Browse", "Progress", "Notes", "Profile", "Settings"}
        for index, step in enumerate(TUTORIAL_STEPS):
            with self.subTest(step=index):
                self.assertTrue(step["title"].strip())
                self.assertTrue(step["body"].strip())
                self.assertTrue(step["detail"].strip())
                self.assertIn(step["route"], valid_routes)


if __name__ == "__main__":
    unittest.main()
