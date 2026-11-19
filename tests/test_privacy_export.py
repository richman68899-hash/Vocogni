"""Tests for the scoped, learner-owned JSON export."""
import json
import unittest

from privacy_export import EXPORT_FORMAT, EXPORT_SCOPE, build_privacy_export_json


class PrivacyExportTests(unittest.TestCase):
    def test_export_preserves_user_data_and_describes_its_scope(self):
        learner_data = {
            "profile": {"name": "Example learner"},
            "progress": {"algebra": {"completed": True}},
            "notes": [{"title": "Revision", "content": "My own notes"}],
        }

        document = json.loads(
            build_privacy_export_json(
                learner_data,
                last_saved_at="2026-11-19T10:00:00+00:00",
                includes_unsaved_changes=True,
            )
        )

        self.assertEqual(document["format"], EXPORT_FORMAT)
        self.assertEqual(document["learner_data"], learner_data)
        self.assertEqual(
            document["last_successful_save_at"],
            "2026-11-19T10:00:00+00:00",
        )
        self.assertTrue(document["includes_unsaved_changes"])
        self.assertIn("identity-provider records", document["scope"])
        self.assertEqual(document["scope"], EXPORT_SCOPE)
        self.assertTrue(document["exported_at"])

    def test_export_does_not_add_identity_claims_or_secrets(self):
        document = json.loads(
            build_privacy_export_json(
                {"profile": {}},
                last_saved_at=None,
                includes_unsaved_changes=False,
            )
        )
        self.assertNotIn("sub", document)
        self.assertNotIn("email", document)
        self.assertNotIn("access_token", document)
        self.assertNotIn("refresh_token", document)

    def test_export_rejects_non_dictionary_data(self):
        with self.assertRaisesRegex(TypeError, "must be a dictionary"):
            build_privacy_export_json(
                ["not", "a", "learner", "bundle"],
                last_saved_at=None,
                includes_unsaved_changes=False,
            )

    def test_export_fails_safely_on_non_json_values(self):
        with self.assertRaisesRegex(ValueError, "could not safely serialize"):
            build_privacy_export_json(
                {"unexpected": object()},
                last_saved_at=None,
                includes_unsaved_changes=False,
            )


if __name__ == "__main__":
    unittest.main()
