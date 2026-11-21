"""Fail-closed policy gate for child learning-profiling (not consent collection).

IMPORTANT: Inputs representing guardian consent, age assurance, legal approval, and
infrastructure verification MUST come from server-verified sources. This module
cannot independently prove those facts. It deliberately fails closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class ConsentState(str, Enum):
    NOT_ASKED = "not_asked"
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    INVALID = "invalid"


class ProfilingData(str, Enum):
    COURSE_PROGRESS = "course_progress"
    ANSWER_OUTCOMES = "answer_outcomes"
    ATTEMPT_COUNTS = "attempt_counts"
    MISCONCEPTION_TAGS = "misconception_tags"
    HINT_LEVEL = "hint_level"
    LEARNER_SELECTED_PREFERENCES = "learner_selected_preferences"
    PROVISIONAL_MASTERY = "provisional_mastery"
    OPTIONAL_PACING_SIGNALS = "optional_pacing_signals"


# The smallest initial allowlist. Pacing signals require a separate feature review.
CORE_LEARNING_DATA: FrozenSet[ProfilingData] = frozenset({
    ProfilingData.COURSE_PROGRESS,
    ProfilingData.ANSWER_OUTCOMES,
    ProfilingData.ATTEMPT_COUNTS,
    ProfilingData.MISCONCEPTION_TAGS,
    ProfilingData.HINT_LEVEL,
    ProfilingData.LEARNER_SELECTED_PREFERENCES,
    ProfilingData.PROVISIONAL_MASTERY,
})


@dataclass(frozen=True)
class ProfilingEvidence:
    """Evidence fields; callers must populate from trusted server-side records."""

    learner_active_request: bool = False
    request_current: bool = False
    request_scope: FrozenSet[ProfilingData] = frozenset()
    learner_is_child: bool = True
    age_assurance_verified: bool = False
    cohort_feature_eligible: bool = False
    guardian_consent_required: bool = True
    guardian_permission: ConsentState = ConsentState.NOT_ASKED
    guardian_verification_complete: bool = False
    legal_article19_review_approved: bool = False
    child_risk_assessment_approved: bool = False
    infrastructure_review_approved: bool = False
    infrastructure_review_current: bool = False


@dataclass(frozen=True)
class ProfilingDecision:
    enabled: bool
    allowed_scope: FrozenSet[ProfilingData]
    reasons: tuple[str, ...]


def evaluate_child_learning_profiling(
    evidence: ProfilingEvidence,
    *,
    allowed_scope: FrozenSet[ProfilingData] = CORE_LEARNING_DATA,
) -> ProfilingDecision:
    """Return enabled only when every required server-side safeguard passes.

    Denial, withdrawal, missing/expired/invalid evidence, a stale infra review,
    unknown age eligibility, or an unapproved legal/risk decision always disable
    profiling. No default profiling and no browser/session consent authority.
    """
    reasons: list[str] = []
    scope = evidence.request_scope & allowed_scope

    if not evidence.learner_active_request:
        reasons.append("learner_has_not_actively_requested_profiling")
    if not evidence.request_current:
        reasons.append("learner_request_missing_stale_or_unverified")
    if not scope:
        reasons.append("no_approved_learning_data_scope_selected")
    if evidence.learner_is_child and not evidence.age_assurance_verified:
        reasons.append("child_age_assurance_not_verified")
    if evidence.learner_is_child and not evidence.cohort_feature_eligible:
        reasons.append("age_cohort_or_feature_eligibility_not_approved")
    if evidence.learner_is_child and evidence.guardian_consent_required:
        if evidence.guardian_permission is not ConsentState.GRANTED:
            reasons.append("required_guardian_permission_not_granted")
        if not evidence.guardian_verification_complete:
            reasons.append("guardian_permission_not_verified")
    if evidence.learner_is_child and not evidence.legal_article19_review_approved:
        reasons.append("child_profiling_legal_review_not_approved")
    if evidence.learner_is_child and not evidence.child_risk_assessment_approved:
        reasons.append("child_risk_assessment_not_approved")
    if not evidence.infrastructure_review_approved:
        reasons.append("infrastructure_review_not_approved")
    if not evidence.infrastructure_review_current:
        reasons.append("infrastructure_review_expired_or_stale")

    if reasons:
        return ProfilingDecision(False, frozenset(), tuple(reasons))

    return ProfilingDecision(True, frozenset(scope), ())


__all__ = [
    "ConsentState",
    "ProfilingData",
    "CORE_LEARNING_DATA",
    "ProfilingEvidence",
    "ProfilingDecision",
    "evaluate_child_learning_profiling",
]
