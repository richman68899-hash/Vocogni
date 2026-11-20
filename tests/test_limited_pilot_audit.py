from __future__ import annotations

import unittest
from datetime import date, timedelta

from scripts.audit_limited_pilot import REQUIRED_REVIEWER_ROLE, validate_manifest


def make_manifest() -> dict:
    start = date.today() + timedelta(days=2)
    end = start + timedelta(days=30)
    evidence = {}
    for key, role in REQUIRED_REVIEWER_ROLE.items():
        evidence[key] = {
            "status": "approved",
            "reviewed_by": "Reviewer",
            "reviewer_role": role,
            "reviewed_on": date.today().isoformat(),
            "evidence_ref": f"secure-record:{key}",
            "scope": f"Reviewed {key}",
        }
    evidence["external_ai_provider_review"].update({
        "status": "not_applicable",
        "reviewer_role": "qualified_indonesian_counsel",
        "rationale": "Counsel reviewed the disabled pilot configuration.",
    })
    evidence["learner_interaction_safety_review"].update({
        "status": "not_applicable",
        "reviewer_role": "qualified_indonesian_counsel",
        "rationale": "No learner-to-learner feature is in scope.",
    })
    return {
        "schema_version": 1,
        "pilot": {
            "name": "Closed mathematics pilot",
            "purpose": "Evaluate a restricted set of lessons.",
            "operator_legal_name": "Adult operator",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "participant_limit": 8,
            "approved_participant_count": 6,
            "age_bands": ["13_15"],
            "recruitment_mode": "invite_only",
            "public_signup_enabled": False,
            "ministerial_risk_profile": "low",
            "article_19_profiling_disposition": "core_feature_actively_requested_by_child",
            "external_ai_tutoring_enabled": False,
            "learner_to_learner_interaction_enabled": False,
            "features_in_scope": ["lessons", "diagnostics", "adaptive_recommendations", "persistent_progress"],
            "release_commit_sha": "a" * 40,
        },
        "evidence": evidence,
    }


class LimitedPilotAuditTests(unittest.TestCase):
    def test_complete_manifest_never_authorizes_release(self):
        report = validate_manifest(make_manifest())
        self.assertEqual(report["blocker_count"], 0)
        self.assertTrue(report["evidence_manifest_complete"])
        self.assertFalse(report["pilot_release_authorized"])

    def test_pending_guardian_consent_blocks(self):
        manifest = make_manifest()
        manifest["evidence"]["guardian_consent_and_withdrawal"]["status"] = "pending"
        report = validate_manifest(manifest)
        self.assertFalse(report["evidence_manifest_complete"])

    def test_high_risk_profile_blocks_under_16(self):
        manifest = make_manifest()
        manifest["pilot"]["ministerial_risk_profile"] = "high"
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.ministerial_risk_profile" for x in report["blockers"]))

    def test_high_risk_profile_is_not_rejected_by_under_16_rule_for_16_to_17(self):
        manifest = make_manifest()
        manifest["pilot"]["age_bands"] = ["16_17"]
        manifest["pilot"]["ministerial_risk_profile"] = "high"
        report = validate_manifest(manifest)
        self.assertFalse(any(x["item"] == "pilot.ministerial_risk_profile" for x in report["blockers"]))

    def test_count_cannot_exceed_cap(self):
        manifest = make_manifest()
        manifest["pilot"]["approved_participant_count"] = 9
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.approved_participant_count" for x in report["blockers"]))

    def test_public_signup_is_blocked(self):
        manifest = make_manifest()
        manifest["pilot"]["public_signup_enabled"] = True
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.public_signup_enabled" for x in report["blockers"]))

    def test_invite_only_is_required(self):
        manifest = make_manifest()
        manifest["pilot"]["recruitment_mode"] = "open"
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.recruitment_mode" for x in report["blockers"]))

    def test_duration_limit_is_enforced(self):
        manifest = make_manifest()
        start = date.today() + timedelta(days=2)
        manifest["pilot"]["start_date"] = start.isoformat()
        manifest["pilot"]["end_date"] = (start + timedelta(days=91)).isoformat()
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.duration" for x in report["blockers"]))

    def test_ai_cannot_be_not_applicable_when_enabled(self):
        manifest = make_manifest()
        manifest["pilot"]["external_ai_tutoring_enabled"] = True
        manifest["pilot"]["features_in_scope"].append("external_ai_tutoring")
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "external_ai_provider_review" for x in report["blockers"]))

    def test_child_safeguard_cannot_be_not_applicable(self):
        manifest = make_manifest()
        entry = manifest["evidence"]["guardian_consent_and_withdrawal"]
        entry.update({"status": "not_applicable", "rationale": "Small pilot"})
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "guardian_consent_and_withdrawal" for x in report["blockers"]))

    def test_wrong_reviewer_role_blocks_legal_decision(self):
        manifest = make_manifest()
        manifest["evidence"]["article_19_child_profiling_analysis"]["reviewer_role"] = "responsible_adult_operator"
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "article_19_child_profiling_analysis" for x in report["blockers"]))

    def test_profiling_cannot_be_disabled_with_adaptive_features_in_scope(self):
        manifest = make_manifest()
        manifest["pilot"]["article_19_profiling_disposition"] = "profiling_disabled_for_pilot"
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.article_19_profiling_disposition" for x in report["blockers"]))

    def test_release_commit_must_be_full_sha(self):
        manifest = make_manifest()
        manifest["pilot"]["release_commit_sha"] = "main"
        report = validate_manifest(manifest)
        self.assertTrue(any(x["item"] == "pilot.release_commit_sha" for x in report["blockers"]))

    def test_invalid_manifest_fails_closed(self):
        report = validate_manifest([])
        self.assertFalse(report["evidence_manifest_complete"])
        self.assertFalse(report["pilot_release_authorized"])


if __name__ == "__main__":
    unittest.main()
