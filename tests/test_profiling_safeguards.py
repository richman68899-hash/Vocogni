import unittest

from profiling_safeguards import (
    CORE_LEARNING_DATA,
    ConsentState,
    ProfilingData,
    ProfilingEvidence,
    evaluate_child_learning_profiling,
)


def fully_approved(**overrides):
    values = dict(
        learner_active_request=True,
        request_current=True,
        request_scope=CORE_LEARNING_DATA,
        learner_is_child=True,
        age_assurance_verified=True,
        cohort_feature_eligible=True,
        guardian_consent_required=True,
        guardian_permission=ConsentState.GRANTED,
        guardian_verification_complete=True,
        legal_article19_review_approved=True,
        child_risk_assessment_approved=True,
        infrastructure_review_approved=True,
        infrastructure_review_current=True,
    )
    values.update(overrides)
    return ProfilingEvidence(**values)


class ChildProfilingGateTests(unittest.TestCase):
    def test_all_gates_pass_enables_only_allowlisted_scope(self):
        decision = evaluate_child_learning_profiling(fully_approved())
        self.assertTrue(decision.enabled)
        self.assertEqual(decision.allowed_scope, CORE_LEARNING_DATA)
        self.assertEqual(decision.reasons, ())

    def test_no_learner_request_means_off(self):
        decision = evaluate_child_learning_profiling(
            fully_approved(learner_active_request=False)
        )
        self.assertFalse(decision.enabled)
        self.assertIn("learner_has_not_actively_requested_profiling", decision.reasons)

    def test_denied_guardian_permission_means_off(self):
        decision = evaluate_child_learning_profiling(
            fully_approved(guardian_permission=ConsentState.DENIED)
        )
        self.assertFalse(decision.enabled)
        self.assertIn("required_guardian_permission_not_granted", decision.reasons)

    def test_withdrawn_guardian_permission_means_off(self):
        decision = evaluate_child_learning_profiling(
            fully_approved(guardian_permission=ConsentState.WITHDRAWN)
        )
        self.assertFalse(decision.enabled)

    def test_unverified_guardian_permission_means_off(self):
        decision = evaluate_child_learning_profiling(
            fully_approved(guardian_verification_complete=False)
        )
        self.assertFalse(decision.enabled)
        self.assertIn("guardian_permission_not_verified", decision.reasons)

    def test_age_assurance_or_cohort_failure_means_off(self):
        for overrides in (
            {"age_assurance_verified": False},
            {"cohort_feature_eligible": False},
        ):
            with self.subTest(overrides=overrides):
                decision = evaluate_child_learning_profiling(
                    fully_approved(**overrides)
                )
                self.assertFalse(decision.enabled)

    def test_legal_or_child_risk_review_missing_means_off(self):
        for overrides in (
            {"legal_article19_review_approved": False},
            {"child_risk_assessment_approved": False},
        ):
            with self.subTest(overrides=overrides):
                decision = evaluate_child_learning_profiling(
                    fully_approved(**overrides)
                )
                self.assertFalse(decision.enabled)

    def test_stale_or_unapproved_infrastructure_means_off(self):
        for overrides in (
            {"infrastructure_review_approved": False},
            {"infrastructure_review_current": False},
        ):
            with self.subTest(overrides=overrides):
                decision = evaluate_child_learning_profiling(
                    fully_approved(**overrides)
                )
                self.assertFalse(decision.enabled)

    def test_empty_scope_means_off(self):
        decision = evaluate_child_learning_profiling(
            fully_approved(request_scope=frozenset())
        )
        self.assertFalse(decision.enabled)

    def test_unapproved_data_categories_are_filtered(self):
        request_scope = CORE_LEARNING_DATA | {ProfilingData.OPTIONAL_PACING_SIGNALS}
        decision = evaluate_child_learning_profiling(
            fully_approved(request_scope=request_scope)
        )
        self.assertTrue(decision.enabled)
        self.assertNotIn(ProfilingData.OPTIONAL_PACING_SIGNALS, decision.allowed_scope)

    def test_all_gates_fail_closed_when_evidence_is_missing(self):
        decision = evaluate_child_learning_profiling(ProfilingEvidence())
        self.assertFalse(decision.enabled)
        self.assertGreater(len(decision.reasons), 5)
        self.assertEqual(decision.allowed_scope, frozenset())


if __name__ == "__main__":
    unittest.main()
