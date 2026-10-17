"""Regression tests for profile gender choices and app version."""

import unittest

import data
from version import APP_VERSION


class ProfileGenderTests(unittest.TestCase):
    def test_gender_options_match_the_requested_profile_choices(self):
        self.assertEqual(
            data.GENDER_OPTIONS,
            ["Male", "Female", "Prefer not to say / others"],
        )

    def test_non_disclosing_choice_is_available(self):
        self.assertEqual(data.GENDER_OPTIONS[2], "Prefer not to say / others")

    def test_app_version_is_a_development_version(self):
        self.assertEqual(APP_VERSION, "1.4.0-dev")
        self.assertIn("dev", APP_VERSION)


if __name__ == "__main__":
    unittest.main()
