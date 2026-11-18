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
                self.assertIsNotNone(release_gate.learner_access_block_reason(environ))

    def test_only_explicit_truthy_values_enable_private_preview(self):
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value):
                environ = {release_gate.PREVIEW_ENV: value}
                self.assertTrue(release_gate.is_private_preview_enabled(environ))
                self.assertIsNone(release_gate.learner_access_block_reason(environ))

    def test_preview_flag_is_not_a_public_release_approval(self):
        reason = release_gate.learner_access_block_reason({})
        self.assertIn("guardian-consent", reason)
        self.assertIn("monitored-support", reason)
        self.assertIn("not open to learners", reason)

    def test_custom_environment_mapping_does_not_read_process_environment(self):
        self.assertFalse(release_gate.is_private_preview_enabled({}))


if __name__ == "__main__":
    unittest.main()
