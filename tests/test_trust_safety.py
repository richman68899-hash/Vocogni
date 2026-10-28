"""Regression tests for Vocogni's policy surfaces and assistant disclosures."""
import unittest

from sections.trust_safety import load_policy
from vocogni_assistant import answer_request


class TrustSafetyPolicyTests(unittest.TestCase):
    def test_all_policy_drafts_are_readable_and_marked_as_drafts(self):
        for key in ("terms", "privacy", "ai_safety"):
            with self.subTest(policy=key):
                content = load_policy(key)
                self.assertTrue(content.strip())
                self.assertIn("Working Draft", content)
                self.assertIn("not", content.casefold())

    def test_policy_drafts_state_that_operator_contact_is_not_configured(self):
        terms = load_policy("terms")
        privacy = load_policy("privacy")
        self.assertIn("not yet confirmed", terms.casefold())
        self.assertIn("not yet configured", terms.casefold())
        self.assertIn("not yet configured", privacy.casefold())

    def test_child_safety_and_guardian_consent_are_explicit(self):
        privacy = load_policy("privacy")
        terms = load_policy("terms")
        self.assertIn("guardian consent", privacy.casefold())
        self.assertIn("parent/guardian consent", terms.casefold())
        self.assertIn("does not", privacy.casefold())

    def test_ai_policy_matches_current_rule_based_assistant(self):
        policy = load_policy("ai_safety")
        self.assertIn("rule-based helper", policy)
        self.assertIn("does not call an external LLM", policy)
        self.assertIn("model-generated questions", policy.casefold())

    def test_assistant_can_open_trust_safety_page(self):
        profile = {}
        progress = {}
        for query in ("open trust & safety", "open terms", "open privacy notice", "open AI use & safety"):
            with self.subTest(query=query):
                reply, route = answer_request(query, profile, progress)
                self.assertEqual(route, "Trust & Safety")
                self.assertIn("Opening", reply)

    def test_assistant_explains_policy_drafts_when_asked(self):
        reply, route = answer_request("terms of service", {}, {})
        self.assertEqual(route, "Trust & Safety")
        self.assertIn("drafts", reply)
        self.assertIn("not legal advice", reply)


if __name__ == "__main__":
    unittest.main()
