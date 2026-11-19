"""Fail-closed release-gate tests; no Streamlit dependency required."""
import unittest

import release_gate


class ReleaseGateTests(unittest.TestCase):
    def test_missing_or_false_flag_blocks_learner_access(self):
        for environ in (
            {},
            {release_gate.PREVIEW_ENV: ""},
            {release_gate.PREVIEW_ENV: "false"},
            {release_gate.PREVIEW_ENV: "0"},
            {release_gate.PREVIEW_ENV: "no"},
            {release_gate.PREVIEW_ENV: "enabled"},
        ):
            with self.subTest(environ=environ):
                self.assertIsNotNone(
                    release_gate.learner_access_block_reason(environ)
                )

    def test_preview_flag_alone_does_not_authorise_any_account(self):
        environ = {release_gate.PREVIEW_ENV: "true"}
        reason = release_gate.learner_access_block_reason(environ)
        self.assertIsNotNone(reason)
        self.assertIn(release_gate.PREVIEW_ALLOWED_SUBJECTS_ENV, reason)

    def test_only_explicit_truthy_values_enable_preview_when_allowlist_exists(self):
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value):
                environ = {
                    release_gate.PREVIEW_ENV: value,
                    release_gate.PREVIEW_ALLOWED_SUBJECTS_ENV: "auth0|tester-1",
                }
                self.assertTrue(release_gate.is_private_preview_enabled(environ))
                # An unauthenticated visitor may reach Auth0, not learner data.
                self.assertIsNone(
                    release_gate.learner_access_block_reason(environ)
                )

    def test_only_exact_allowlisted_oidc_subject_can_enter(self):
        environ = {
            release_gate.PREVIEW_ENV: "1",
            release_gate.PREVIEW_ALLOWED_SUBJECTS_ENV: "auth0|tester-1,auth0|tester-2",
        }
        self.assertIsNone(
            release_gate.learner_access_block_reason(
                environ,
                is_logged_in=True,
                authenticated_subject="auth0|tester-1",
            )
        )
        for subject in ("auth0|tester-3", "tester-1", "AUTH0|tester-1", "", None):
            with self.subTest(subject=subject):
                self.assertIsNotNone(
                    release_gate.learner_access_block_reason(
                        environ,
                        is_logged_in=True,
                        authenticated_subject=subject,
                    )
                )

    def test_allowlist_parser_trims_and_ignores_empty_entries(self):
        environ = {
            release_gate.PREVIEW_ALLOWED_SUBJECTS_ENV:
                " auth0|one, ,auth0|two;\nauth0|three ",
        }
        self.assertEqual(
            release_gate.get_preview_allowed_subjects(environ),
            frozenset({"auth0|one", "auth0|two", "auth0|three"}),
        )

    def test_logged_in_account_without_subject_is_blocked(self):
        environ = {
            release_gate.PREVIEW_ENV: "true",
            release_gate.PREVIEW_ALLOWED_SUBJECTS_ENV: "auth0|tester-1",
        }
        reason = release_gate.learner_access_block_reason(
            environ, is_logged_in=True, authenticated_subject=None
        )
        self.assertIsNotNone(reason)
        self.assertIn("not authorised", reason)

    def test_preview_block_message_does_not_claim_legal_clearance(self):
        reason = release_gate.learner_access_block_reason({})
        self.assertIn("guardian-consent", reason)
        self.assertIn("monitored-support", reason)
        self.assertIn("not open to learners", reason)

    def test_custom_environment_mapping_does_not_read_process_environment(self):
        self.assertFalse(release_gate.is_private_preview_enabled({}))
        self.assertEqual(release_gate.get_preview_allowed_subjects({}), frozenset())


if __name__ == "__main__":
    unittest.main()
