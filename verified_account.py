"""Owner-only verified badge helpers for Vocogni.

The badge is granted by the authenticated OIDC subject, never by a display
name, profile name, or email string. The allowlisted subject is configured
outside source control as VOCogni_VERIFIED_USER_SUB.
"""
from __future__ import annotations

import base64
import hmac
import os
from pathlib import Path

import streamlit as st


VERIFIED_SUBJECT_SETTING = "VOCogni_VERIFIED_USER_SUB"
_BADGE_ASSET = Path(__file__).resolve().parent / "assets" / "verified_badge.svg"


def is_verified_subject(actual_subject: object, configured_subject: object) -> bool:
    """Return True only when both non-empty OIDC subject IDs match exactly."""
    if not isinstance(actual_subject, str) or not isinstance(configured_subject, str):
        return False
    actual = actual_subject.strip()
    expected = configured_subject.strip()
    if not actual or not expected:
        return False
    return hmac.compare_digest(actual, expected)


def _configured_verified_subject() -> str:
    """Read the owner allowlist from Streamlit Secrets, then environment."""
    configured = ""
    try:
        configured = str(st.secrets.get(VERIFIED_SUBJECT_SETTING, "") or "").strip()
    except Exception:
        configured = ""
    if configured:
        return configured
    return os.environ.get(VERIFIED_SUBJECT_SETTING, "").strip()


def is_current_account_verified() -> bool:
    """Check the current Auth0/OIDC subject. Fail closed when unavailable."""
    try:
        actual_subject = st.user.get("sub", "")
    except Exception:
        return False
    return is_verified_subject(actual_subject, _configured_verified_subject())


def verified_badge_html(size: int = 20) -> str:
    """Return the original transparent SVG as a compact, accessible image."""
    try:
        pixel_size = int(size)
    except (TypeError, ValueError):
        pixel_size = 20
    pixel_size = max(14, min(32, pixel_size))

    svg = _BADGE_ASSET.read_text(encoding="utf-8")
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return (
        f"<img class='vc-verified-badge' "
        f"src='data:image/svg+xml;base64,{encoded}' "
        f"width='{pixel_size}' height='{pixel_size}' "
        "alt='Verified Vocogni owner account' "
        "title='Verified Vocogni owner account' "
        "style='display:inline-block;flex:0 0 auto;width:"
        f"{pixel_size}px;height:{pixel_size}px;object-fit:contain;vertical-align:middle;' "
        "/>"
    )
