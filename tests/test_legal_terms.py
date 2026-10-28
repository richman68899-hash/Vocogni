"""Contract tests for the bilingual Terms of Service and its app wiring."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMS = (ROOT / "TERMS_OF_SERVICE.md").read_text(encoding="utf-8")
LEGAL_SOURCE = (ROOT / "sections" / "legal.py").read_text(encoding="utf-8")
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
CHECKLIST = (ROOT / "docs" / "LEGAL_LAUNCH_CHECKLIST.md").read_text(encoding="utf-8")


class LegalTermsTests(unittest.TestCase):
    def test_bilingual_terms_sections_exist(self):
        self.assertIn("<!-- ENGLISH_START -->", TERMS)
        self.assertIn("<!-- INDONESIAN_START -->", TERMS)
        self.assertIn("<!-- END_TERMS -->", TERMS)
        self.assertIn("# Vocogni Terms of Service", TERMS)
        self.assertIn("# Ketentuan Layanan Vocogni", TERMS)

    def test_terms_cover_child_consent_and_ai_limitations(self):
        self.assertIn("parent or guardian consent", TERMS.lower())
        self.assertIn("persetujuan orang tua/wali", TERMS.lower())
        self.assertIn("not an official school grade", TERMS.lower())
        self.assertIn("nilai resmi sekolah", TERMS.lower())

    def test_operator_and_privacy_placeholders_are_explicit(self):
        self.assertIn("[INSERT THE FULL LEGAL NAME OF THE OPERATOR]", TERMS)
        self.assertIn("[INSERT A MONITORED SUPPORT AND PRIVACY CONTACT EMAIL]", TERMS)
        self.assertIn("Privacy Notice", TERMS)
        self.assertIn("Pemberitahuan Privasi", TERMS)

    def test_terms_are_accessible_before_login_and_after_login(self):
        self.assertIn("legal_section.render_embedded()", APP_SOURCE)
        self.assertIn('"Legal": legal_section.render', APP_SOURCE)
        self.assertIn('("Terms", "Legal")', APP_SOURCE)
        self.assertIn("def render_embedded()", LEGAL_SOURCE)

    def test_launch_checklist_does_not_claim_compliance(self):
        self.assertIn("not publication-ready", CHECKLIST)
        self.assertIn("No acceptance record or guardian-consent verification", CHECKLIST)
        self.assertIn("Regulation No. 9 of 2026", CHECKLIST)


if __name__ == "__main__":
    unittest.main()
