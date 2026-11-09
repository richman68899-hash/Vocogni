"""Tests for owner-only verified badge identity and asset handling."""
import unittest
from pathlib import Path

from verified_account import (
    _BADGE_ASSET,
    is_verified_subject,
    verified_badge_html,
)


class VerifiedAccountTests(unittest.TestCase):
    def test_only_exact_non_empty_oidc_subject_matches(self):
        self.assertTrue(is_verified_subject("auth0|owner-123", "auth0|owner-123"))
        self.assertFalse(is_verified_subject("auth0|learner-456", "auth0|owner-123"))
        self.assertFalse(is_verified_subject("", "auth0|owner-123"))
        self.assertFalse(is_verified_subject("auth0|owner-123", ""))
        self.assertFalse(is_verified_subject(None, "auth0|owner-123"))

    def test_display_name_is_not_a_verification_identifier(self):
        self.assertFalse(is_verified_subject("John Cena", "auth0|owner-123"))

    def test_badge_svg_has_transparent_background_and_no_embedded_white_canvas(self):
        svg = _BADGE_ASSET.read_text(encoding="utf-8")
        self.assertIn('viewBox="0 0 64 64"', svg)
        self.assertIn('fill="#0795B8"', svg)
        self.assertIn('stroke="#FFFFFF"', svg)
        self.assertNotIn("<rect", svg.lower())
        self.assertNotIn("background", svg.lower())

    def test_badge_markup_uses_svg_data_uri_and_accessible_alt_text(self):
        markup = verified_badge_html(22)
        self.assertIn("data:image/svg+xml;base64,", markup)
        self.assertIn("alt='Vocogni owner account'", markup)
        self.assertIn("width='22' height='22'", markup)

    def test_badge_size_is_clamped(self):
        markup = verified_badge_html(200)
        self.assertIn("width='32' height='32'", markup)
        markup = verified_badge_html(1)
        self.assertIn("width='14' height='14'", markup)


if __name__ == "__main__":
    unittest.main()
