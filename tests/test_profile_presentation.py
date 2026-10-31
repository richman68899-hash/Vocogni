"""Regression tests for the learner-profile presentation helpers."""

import base64
import io
import unittest

from PIL import Image

from profile_presentation import (
    display_profile_value,
    profile_icon_svg,
    profile_initials,
    process_profile_avatar,
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

    def test_avatar_processing_returns_transparent_circular_png(self):
        source = Image.new("RGB", (400, 200), "red")
        buffer = io.BytesIO()
        source.save(buffer, format="PNG")

        data_uri = process_profile_avatar(buffer.getvalue())
        self.assertTrue(data_uri.startswith("data:image/png;base64,"))
        image_bytes = base64.b64decode(data_uri.split(",", 1)[1])
        with Image.open(io.BytesIO(image_bytes)) as avatar:
            self.assertEqual(avatar.size, (256, 256))
            self.assertEqual(avatar.mode, "RGBA")
            self.assertEqual(avatar.getpixel((0, 0))[3], 0)
            self.assertEqual(avatar.getpixel((128, 128))[3], 255)

    def test_avatar_processing_rejects_invalid_and_oversized_files(self):
        with self.assertRaises(ValueError):
            process_profile_avatar(b"not an image")
        with self.assertRaises(ValueError):
            process_profile_avatar(b"x" * 100, max_bytes=50)


if __name__ == "__main__":
    unittest.main()
