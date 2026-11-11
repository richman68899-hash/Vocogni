from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PrivacyPolicyDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = (ROOT / "PRIVACY_POLICY.md").read_text(encoding="utf-8")
        cls.checklist = (
            ROOT / "docs" / "legal" / "privacy-policy-release-checklist.md"
        ).read_text(encoding="utf-8")

    def test_policy_covers_the_live_data_flows(self):
        for phrase in (
            "Auth0",
            "Supabase",
            "Streamlit",
            "Google Fonts",
            "assistant conversation",
            "notes",
            "milestones",
            "retention",
            "data rights",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.casefold(), self.policy.casefold())

    def test_policy_does_not_claim_children_are_already_supported(self):
        self.assertIn("does not establish that it identifies child users", self.policy)
        self.assertIn("not parental consent", self.policy)

    def test_policy_discloses_optional_external_ai_tutoring_accurately(self):
        text = self.policy.casefold()
        for phrase in (
            "optional external ai tutoring",
            "session-only learner opt-in",
            "up to eight messages",
            "limited learning-context summary",
            "configured external provider",
            "does not verify or record parent/guardian consent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertNotIn("does not currently call a third-party generative-ai model", text)

    def test_launch_checklist_describes_the_operator_gate_for_external_ai(self):
        readiness = (ROOT / "docs" / "legal" / "launch-readiness.md").read_text(encoding="utf-8").casefold()
        self.assertIn("server-side operator enablement", readiness)
        self.assertIn("session-only learner opt-in", readiness)
        self.assertIn("limited learning-context summary", readiness)

    def test_unresolved_release_items_are_explicit(self):
        for marker in (
            "[INSERT FULL LEGAL NAME OR LEGAL ENTITY]",
            "[INSERT MONITORED PRIVACY EMAIL ADDRESS]",
            "[INSERT POSTAL OR BUSINESS ADDRESS]",
            "does not yet define and enforce a complete, published retention schedule",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.policy)

        self.assertIn("Children's data — release blocker", self.checklist)
        self.assertIn("do not launch", self.checklist.casefold())


if __name__ == "__main__":
    unittest.main()
