"""Fail-closed release gate for the child-facing learning prototype.

The repository does not yet contain a verified guardian-consent workflow,
monitored safeguarding contact, or completed legal/operator review. Therefore
normal learner access is disabled. A private operator preview may be enabled
explicitly for synthetic-data testing; this flag is not a public-launch approval.
"""
from __future__ import annotations

import os
from typing import Mapping

PREVIEW_ENV = "VOCogni_INTERNAL_PREVIEW"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def is_private_preview_enabled(environ: Mapping[str, str] | None = None) -> bool:
    """Return True only for an explicit private-preview opt-in.

    Missing, malformed, or false values fail closed. Callers must keep the
    preview deployment access-restricted and use synthetic learner data.
    """
    source = os.environ if environ is None else environ
    value = str(source.get(PREVIEW_ENV, "") or "").strip().casefold()
    return value in _TRUE_VALUES


def learner_access_block_reason(environ: Mapping[str, str] | None = None) -> str | None:
    """Return the release-block message unless an operator preview is enabled."""
    if is_private_preview_enabled(environ):
        return None
    return (
        "Vocogni is not open to learners yet. This prototype is in a restricted "
        "pre-launch state while child-safety, privacy, guardian-consent, and "
        "monitored-support requirements are completed. No learner account or "
        "learning data was loaded. Please contact the person operating Vocogni "
        "through the channel that provided this link."
    )


__all__ = [
    "PREVIEW_ENV",
    "is_private_preview_enabled",
    "learner_access_block_reason",
]
