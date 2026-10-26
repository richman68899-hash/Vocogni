"""Regression tests for the learner-profile presentation helpers."""

import unittest

from profile_presentation import (
    display_profile_value,
    profile_icon_svg,
    profile_initials,
)


class ProfilePresentationTests(unittest.TestCase):
    def test_initials_use_first_and_last_name(self):
        self.assertEqual(profile_initials("Ada Lovelace"), "AL")
        self.assertEqual(profile_initials("Ada Byron Lovelace"), "AL")

    def test_initials_handle_blank_and_single_names(self):
        self.assertEqual(profile_initials(""), "L")
        self.assertEqual(profile_initials(None), "L")
        self.assertEqual(profile_initials("Vocogni"), "V")

    def test_profile_values_are_html_escaped(self):
        self.assertEqual(
            display_profile_value("<script>alert(1)</script>"),
            "&lt;script&gt;alert(1)&lt;/script&gt;",
        )

    def test_list_values_are_displayed_without_raw_html(self):
        self.assertEqual(
            display_profile_value(["Math", "<Biology>"]),
            "Math, &lt;Biology&gt;",
        )

    def test_section_icons_are_accessible_decorative_svg(self):
        for icon_name in ("user", "book", "target", "spark", "shield"):
            with self.subTest(icon_name=icon_name):
                svg = profile_icon_svg(icon_name)
                self.assertIn("<svg", svg)
                self.assertIn('aria-hidden="true"', svg)
                self.assertIn("stroke-linecap", svg)


if __name__ == "__main__":
    unittest.main()
