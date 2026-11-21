"""Tests for the legal-system control-register audit."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from scripts.audit_legal_system import (
    REQUIRED_CONTROLS,
    REQUIRED_DOCUMENTS,
    validate_register,
)


class LegalSystemAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def pending_register(self):
        return {
            "schema_version": 1,
            "release": {
                "release_name": "Synthetic test release",
                "release_commit_sha": "a" * 40,
                "environment_reference": "synthetic-test-environment",
                "intended_age_bands": ["13_15"],
                "feature_scope": ["synthetic-only"],
                "review_cycle": "test-only",
            },
            "controls": {
                key: {"control_id": details[0], "status": "pending"}
                for key, details in REQUIRED_CONTROLS.items()
            },
        }

    def fully_documented_register(self):
        register = self.pending_register()
        today = date.today()
        for key, (control_id, required_role, na_allowed) in REQUIRED_CONTROLS.items():
            entry = {
                "control_id": control_id,
                "status": "approved",
                "reviewed_by": "Synthetic reviewer",
                "reviewer_role": required_role,
                "reviewed_on": today.isoformat(),
                "review_due": (today + timedelta(days=30)).isoformat(),
                "evidence_ref": "synthetic-evidence-index#unit-test",
                "scope": "Synthetic unit-test fixture only",
                "reviewed_commit_sha": "b" * 40,
            }
            register["controls"][key] = entry
        return register

    def test_template_style_pending_register_is_blocked(self):
        report = validate_register(self.pending_register(), self.root)
        self.assertFalse(report["control_register_complete_for_human_review"])
        self.assertFalse(report["release_authorized"])
        self.assertEqual(report["approved_count"], 0)
        self.assertEqual(report["resolved_count"], 0)
        self.assertGreater(report["blocker_count"], 0)

    def test_record_completeness_never_authorizes_release(self):
        report = validate_register(self.fully_documented_register(), self.root)
        self.assertTrue(report["control_register_complete_for_human_review"])
        self.assertFalse(report["release_authorized"])
        self.assertEqual(report["approved_count"], len(REQUIRED_CONTROLS))

    def test_wrong_reviewer_role_blocks_control(self):
        register = self.fully_documented_register()
        register["controls"]["guardian_authorisation"]["reviewer_role"] = "product_owner"
        report = validate_register(register, self.root)
        self.assertFalse(report["control_register_complete_for_human_review"])
        self.assertTrue(any(x["item"] == "guardian_authorisation" for x in report["blockers"]))

    def test_not_applicable_is_rejected_for_mandatory_child_controls(self):
        register = self.fully_documented_register()
        entry = register["controls"]["guardian_authorisation"]
        entry.update({
            "status": "not_applicable",
            "rationale": "Synthetic invalid rationale",
        })
        report = validate_register(register, self.root)
        self.assertTrue(any(x["item"] == "guardian_authorisation" for x in report["blockers"]))

    def test_not_applicable_requires_counsel_and_rationale_for_optional_ai(self):
        register = self.fully_documented_register()
        entry = register["controls"]["external_ai_review"]
        entry.update({"status": "not_applicable", "rationale": "No external AI in this synthetic release."})
        report = validate_register(register, self.root)
        self.assertTrue(report["control_register_complete_for_human_review"])
        entry["rationale"] = ""
        report = validate_register(register, self.root)
        self.assertTrue(any(x["item"] == "external_ai_review" for x in report["blockers"]))

    def test_stale_review_date_blocks(self):
        register = self.fully_documented_register()
        register["controls"]["privacy_notice"]["review_due"] = date.today().isoformat()
        report = validate_register(register, self.root)
        self.assertTrue(any(x["item"] == "privacy_notice" for x in report["blockers"]))

    def test_future_reviewed_date_blocks(self):
        register = self.fully_documented_register()
        register["controls"]["privacy_notice"]["reviewed_on"] = (date.today() + timedelta(days=1)).isoformat()
        report = validate_register(register, self.root)
        self.assertTrue(any(x["item"] == "privacy_notice" for x in report["blockers"]))

    def test_invalid_commit_sha_blocks(self):
        register = self.fully_documented_register()
        register["controls"]["database_and_account_isolation"]["reviewed_commit_sha"] = "not-a-sha"
        report = validate_register(register, self.root)
        self.assertTrue(any(x["item"] == "database_and_account_isolation" for x in report["blockers"]))

    def test_missing_mandatory_document_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            report = validate_register(self.fully_documented_register(), Path(temp))
        self.assertFalse(report["control_register_complete_for_human_review"])
        self.assertTrue(any(x["item"] == REQUIRED_DOCUMENTS[0] for x in report["blockers"]))

    def test_unknown_control_is_warned(self):
        register = self.fully_documented_register()
        register["controls"]["surprise_control"] = {"status": "approved"}
        report = validate_register(register, self.root)
        self.assertEqual(report["warning_count"], 1)
        self.assertFalse(report["control_register_complete_for_human_review"])

    def test_template_and_readme_do_not_claim_legal_clearance(self):
        manual = (self.root / "docs/legal/compliance-operating-system.md").read_text(encoding="utf-8")
        self.assertIn("not legal clearance", manual.casefold())
        self.assertIn("NO-GO", manual)
        self.assertFalse(validate_register(self.pending_register(), self.root)["release_authorized"])


if __name__ == "__main__":
    unittest.main()
