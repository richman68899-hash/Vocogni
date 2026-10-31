"""Regression checks for the in-app terms, privacy, and AI-safety notices."""
import unittest

from legal_notices import NOTICE_FILES, NOTICE_SUMMARIES, load_notice


class LegalNoticeTests(unittest.TestCase):
    def test_all_user_facing_notices_exist_and_have_draft_status(self):
        self.assertEqual(set(NOTICE_FILES), {"terms", "privacy", "ai_safety"})
        for name in NOTICE_FILES:
            with self.subTest(notice=name):
                text = load_notice(name)
                self.assertTrue(text.strip())
                self.assertIn("draft", text[:500].casefold())

    def test_each_notice_has_a_plain_language_quick_read(self):
        self.assertEqual(set(NOTICE_SUMMARIES), set(NOTICE_FILES))
        for name, summary in NOTICE_SUMMARIES.items():
            with self.subTest(notice=name):
                self.assertIn("Quick read", summary)
                self.assertGreaterEqual(len(summary.splitlines()), 4)

    def test_contact_placeholders_are_explicit_launch_blockers_not_fake_addresses(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "docs" / "legal"
        for filename in ("terms-of-service.md", "privacy-notice.md", "ai-use-and-safety.md"):
            text = (root / filename).read_text(encoding="utf-8").casefold()
            with self.subTest(filename=filename):
                self.assertNotIn("[insert", text)
                self.assertIn("not configured", text)
                self.assertIn("draft", text[:500])

    def test_terms_do_not_claim_official_assessment_or_guaranteed_accuracy(self):
        text = load_notice("terms").casefold()
        self.assertIn("educational limitations", text)
        self.assertIn("official grades", text)
        self.assertIn("prototype", text)

    def test_privacy_notice_matches_current_ai_architecture(self):
        text = load_notice("privacy").casefold()
        self.assertIn("auth0", text)
        self.assertIn("supabase", text)
        self.assertIn("do not require an external generative ai request", text)
        self.assertIn("open-ended ai tutoring is optional and off by default", text)
        self.assertIn("up to eight recent chat messages", text)
        self.assertIn("retention", text)
        self.assertIn("children", text)

    def test_ai_safety_notes_discourage_sensitive_data_and_overreliance(self):
        text = load_notice("ai_safety").casefold()
        self.assertIn("optional ai tutoring", text)
        self.assertIn("disabled by default", text)
        self.assertIn("session-only opt-in", text)
        self.assertIn("passwords", text)
        self.assertIn("academic-integrity", text)
        self.assertIn("human moderator", text)
        self.assertIn("public child-facing use should remain blocked", text)

    def test_indonesian_child_protection_requirements_are_flagged_for_review(self):
        privacy = load_notice("privacy").casefold()
        ai_safety = load_notice("ai_safety").casefold()
        self.assertIn("law no. 27 of 2022", privacy)
        self.assertIn("government regulation no. 17 of 2025", privacy)
        self.assertIn("regulation no. 9 of 2026", privacy)
        self.assertIn("does not verify or record parent/guardian consent", privacy)
        self.assertIn("public child-facing use should remain blocked", ai_safety)

    def test_internal_launch_checklist_flags_missing_operator_and_contact(self):
        from pathlib import Path

        path = Path(__file__).resolve().parents[1] / "docs" / "legal" / "launch-readiness.md"
        text = path.read_text(encoding="utf-8").casefold()
        self.assertIn("legal name", text)
        self.assertIn("monitored", text)
        self.assertIn("retention", text)
        self.assertIn("guardian", text)
        self.assertIn("risk classification", text)
        self.assertIn("2026", text)


if __name__ == "__main__":
    unittest.main()
