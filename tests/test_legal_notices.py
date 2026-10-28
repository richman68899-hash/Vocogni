"""Regression checks for the in-app terms, privacy, and AI-safety notices."""
import unittest

from legal_notices import NOTICE_FILES, load_notice


class LegalNoticeTests(unittest.TestCase):
    def test_all_user_facing_notices_exist_and_have_draft_status(self):
        self.assertEqual(set(NOTICE_FILES), {"terms", "privacy", "ai_safety"})
        for name in NOTICE_FILES:
            with self.subTest(notice=name):
                text = load_notice(name)
                self.assertTrue(text.strip())
                self.assertIn("Draft", text[:500])

    def test_terms_do_not_claim_official_assessment_or_guaranteed_accuracy(self):
        text = load_notice("terms").casefold()
        self.assertIn("educational limitations", text)
        self.assertIn("official grades", text)
        self.assertIn("prototype", text)

    def test_privacy_notice_matches_current_ai_architecture(self):
        text = load_notice("privacy notice".replace(" notice", "")).casefold()
        self.assertIn("auth0", text)
        self.assertIn("supabase", text)
        self.assertIn("does not make a request to an external generative ai model", text)
        self.assertIn("retention", text)
        self.assertIn("children", text)

    def test_ai_safety_notes_discourage_sensitive_data_and_overreliance(self):
        text = load_notice("ai_safety").casefold()
        self.assertIn("does not currently use a connected generative ai model", text)
        self.assertIn("passwords", text)
        self.assertIn("academic-integrity", text)
        self.assertIn("human moderator", text)
        self.assertIn("before any future generative ai integration", text)

    def test_internal_launch_checklist_flags_missing_operator_and_contact(self):
        from pathlib import Path

        path = Path(__file__).resolve().parents[1] / "docs" / "legal" / "launch-readiness.md"
        text = path.read_text(encoding="utf-8").casefold()
        self.assertIn("legal name", text)
        self.assertIn("monitored", text)
        self.assertIn("retention", text)
        self.assertIn("guardian", text)


if __name__ == "__main__":
    unittest.main()
