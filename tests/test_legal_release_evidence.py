"""Tests for the release evidence checklist integrity audit."""
import unittest
from datetime import date, timedelta

from scripts.audit_legal_release_evidence import REQUIRED_ITEMS, validate_manifest


def pending_manifest():
    return {"schema_version": 1, "items": {key: {"status": "pending"} for key in REQUIRED_ITEMS}}


def approved_manifest():
    return {
        "schema_version": 1,
        "items": {
            key: {
                "status": "approved",
                "reviewed_by": "Adult reviewer (test fixture)",
                "reviewer_role": "adult_operator",
                "reviewed_on": date.today().isoformat(),
                "evidence_ref": "private-evidence-index#test",
                "scope": "Synthetic test fixture",
            }
            for key in REQUIRED_ITEMS
        },
    }


class ReleaseEvidenceAuditTests(unittest.TestCase):
    def test_template_is_blocked_until_evidence_is_reviewed(self):
        report = validate_manifest(pending_manifest())
        self.assertEqual(report["approved_count"], 0)
        self.assertEqual(report["resolved_count"], 0)
        self.assertEqual(report["blocker_count"], len(REQUIRED_ITEMS))
        self.assertFalse(report["ready_for_adult_legal_and_operator_review"])

    def test_complete_metadata_passes_integrity_not_compliance_claim(self):
        report = validate_manifest(approved_manifest())
        self.assertEqual(report["blocker_count"], 0)
        self.assertEqual(report["approved_count"], len(REQUIRED_ITEMS))
        self.assertTrue(report["ready_for_adult_legal_and_operator_review"])
        self.assertTrue(any("not legal clearance" in note for note in report["limitations"]))

    def test_missing_review_metadata_blocks(self):
        manifest = approved_manifest()
        manifest["items"]["guardian_consent"].pop("reviewed_by")
        report = validate_manifest(manifest)
        self.assertTrue(any(item["item"] == "guardian_consent" for item in report["blockers"]))

    def test_not_applicable_is_disallowed_for_child_safeguard_items(self):
        manifest = approved_manifest()
        manifest["items"]["guardian_consent"] = {
            "status": "not_applicable", "rationale": "Test reason",
            "reviewer_role": "qualified_indonesian_counsel",
            "reviewed_by": "Test counsel", "reviewed_on": date.today().isoformat(),
            "evidence_ref": "private-index#test", "scope": "Synthetic",
        }
        report = validate_manifest(manifest)
        self.assertTrue(any(item["item"] == "guardian_consent" for item in report["blockers"]))

    def test_external_ai_na_requires_counsel_rationale_and_metadata(self):
        manifest = approved_manifest()
        manifest["items"]["external_ai_review"] = {
            "status": "not_applicable",
            "rationale": "Test-only rationale: no external AI in this release.",
            "reviewer_role": "qualified_indonesian_counsel",
            "reviewed_by": "Test counsel",
            "reviewed_on": date.today().isoformat(),
            "evidence_ref": "private-index#test",
            "scope": "Synthetic",
        }
        report = validate_manifest(manifest)
        self.assertEqual(report["blocker_count"], 0)
        self.assertEqual(report["approved_count"], len(REQUIRED_ITEMS) - 1)
        self.assertEqual(report["resolved_count"], len(REQUIRED_ITEMS))

    def test_not_applicable_without_rationale_blocks(self):
        manifest = approved_manifest()
        manifest["items"]["external_ai_review"]["status"] = "not_applicable"
        report = validate_manifest(manifest)
        self.assertTrue(any(item["item"] == "external_ai_review" for item in report["blockers"]))

    def test_future_review_date_blocks(self):
        manifest = approved_manifest()
        manifest["items"]["responsible_operator"]["reviewed_on"] = (date.today() + timedelta(days=1)).isoformat()
        report = validate_manifest(manifest)
        self.assertTrue(any(item["item"] == "responsible_operator" for item in report["blockers"]))

    def test_unknown_items_are_warned_and_never_count_as_approved(self):
        manifest = approved_manifest()
        manifest["items"]["unknown"] = {"status": "approved"}
        report = validate_manifest(manifest)
        self.assertEqual(report["approved_count"], len(REQUIRED_ITEMS))
        self.assertEqual(report["warning_count"], 1)
        self.assertFalse(report["ready_for_adult_legal_and_operator_review"])

    def test_invalid_shape_fails_closed(self):
        report = validate_manifest([])
        self.assertFalse(report["ready_for_adult_legal_and_operator_review"])
        self.assertEqual(report["blocker_count"], len(REQUIRED_ITEMS))


if __name__ == "__main__":
    unittest.main()
