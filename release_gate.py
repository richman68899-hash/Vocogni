"""Fail-closed release gate for Vocogni's child-facing learning prototype.

Normal learner access stays disabled until the responsible operator has completed
the legal, privacy, consent, safeguarding, and support release requirements.

A private preview is a separate, restricted mode. It requires BOTH an explicit
server-side preview flag and an exact allowlist of OIDC subject IDs. The flag
alone must never grant access to every account in the identity provider.
"""
from __future__ import annotations

import os
import re
from typing import Mapping

PREVIEW_ENV = "VOCogni_INTERNAL_PREVIEW"
PREVIEW_ALLOWED_SUBJECTS_ENV = "VOCogni_INTERNAL_PREVIEW_ALLOWED_SUBJECTS"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _read_setting(name: str, environ: Mapping[str, str] | None = None) -> str:
    """Read a server-side setting; an injected mapping keeps tests deterministic."""
    if environ is not None:
        value = environ.get(name, "")
    else:
        value = os.environ.get(name)
        if value is None:
            # Streamlit secrets are server-side. Keep this optional so this module
            # remains importable in lightweight tests and local tooling.
            try:
                import streamlit as st
                value = st.secrets.get(name, "")
            except Exception:
                value = ""

    return value.strip() if isinstance(value, str) else ""


def is_private_preview_enabled(environ: Mapping[str, str] | None = None) -> bool:
    """Return True only for an explicit private-preview opt-in."""
    value = _read_setting(PREVIEW_ENV, environ).casefold()
    return value in _TRUE_VALUES


def get_preview_allowed_subjects(
    environ: Mapping[str, str] | None = None,
) -> frozenset[str]:
    """Return exact OIDC subject IDs allowed into the private preview.

    Configure a comma-separated list in server-side environment variables or
    Streamlit secrets. Email addresses, display names, wildcard entries, and
    partial matches are deliberately not supported.
    """
    raw = _read_setting(PREVIEW_ALLOWED_SUBJECTS_ENV, environ)
    return frozenset(
        subject.strip()
        for subject in re.split(r"[,;\r\n]+", raw)
        if subject.strip()
    )


def learner_access_block_reason(
    environ: Mapping[str, str] | None = None,
    *,
    is_logged_in: bool = False,
    authenticated_subject: object = None,
) -> str | None:
    """Return a block reason unless access is a named private-preview account.

    When preview is correctly configured but the visitor is not yet signed in,
    return None only to allow the authentication entry screen to render. The
    application calls this gate again after authentication and before loading
    any learner data.
    """
    if not is_private_preview_enabled(environ):
        return (
            "Vocogni is not open to learners yet. The restricted pre-launch "
            "gate remains active while privacy, guardian-consent, child-safety, "
            "and monitored-support requirements are completed. No learner "
            "account or learning data was loaded."
        )

    allowed_subjects = get_preview_allowed_subjects(environ)
    if not allowed_subjects:
        return (
            "Private preview is not configured safely. The operator must set "
            f"{PREVIEW_ALLOWED_SUBJECTS_ENV} to an explicit comma-separated "
            "allowlist of invited OIDC subject IDs. The preview flag alone "
            "does not authorize access."
        )

    if not is_logged_in:
        # Only the login screen may render here. No learner state has been read.
        return None

    subject = authenticated_subject.strip() if isinstance(authenticated_subject, str) else ""
    if not subject or subject not in allowed_subjects:
        return (
            "This account is not authorised for the restricted Vocogni preview. "
            "No learner account or learning data was loaded. Sign out and use "
            "an invited test account."
        )

    return None


__all__ = [
    "PREVIEW_ENV",
    "PREVIEW_ALLOWED_SUBJECTS_ENV",
    "is_private_preview_enabled",
    "get_preview_allowed_subjects",
    "learner_access_block_reason",
]
