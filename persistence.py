"""
persistence.py — VOCogni Version 1.1.0 persistence layer.

Architecture:

    Auth0 / Google
          ↓
    Streamlit OIDC
          ↓
       st.user
          ↓
    this module
          ↓
       Supabase

Responsibilities:
- identify the authenticated learner
- connect to Supabase using a server-side key
- load durable learner state
- save durable learner state

This module does NOT:
- manage passwords
- perform login/signup
- use Supabase Auth sessions
- store OAuth refresh tokens
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client


# ---------------------------------------------------------------------------
# AUTHENTICATION HELPERS
# ---------------------------------------------------------------------------

def _is_logged_in() -> bool:
    """
    Safely determine whether Streamlit has an authenticated OIDC user.

    Current Streamlit exposes st.user.is_logged_in. The fallback exists
    purely for compatibility with dict-like st.user implementations.
    """

    user = st.user

    try:
        return bool(user.is_logged_in)
    except AttributeError:
        try:
            claims = dict(user)
        except (TypeError, ValueError):
            return False

        return bool(claims.get("sub"))


def get_user_id() -> str:
    """
    Return the stable OIDC subject identifier for the current learner.

    This is the value stored in learner_progress.user_id.

    When Google is connected through Auth0, the exact value will normally
    look like a provider-scoped subject such as:

        google-oauth2|...

    Do not replace this with the learner's email.
    """

    if not _is_logged_in():
        raise RuntimeError(
            "No authenticated Vocogni user is available."
        )

    user = st.user

    # Prefer Streamlit's explicit dictionary conversion.
    try:
        claims = user.to_dict()
    except AttributeError:
        try:
            claims = dict(user)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "Could not read the authenticated OIDC user."
            ) from exc

    if not isinstance(claims, dict):
        raise RuntimeError(
            "The authenticated OIDC user has an invalid format."
        )

    user_id = claims.get("sub")

    if not user_id:
        raise RuntimeError(
            "The authenticated user has no OIDC subject "
            "(sub) claim."
        )

    return str(user_id)


# ---------------------------------------------------------------------------
# SUPABASE CLIENT
# ---------------------------------------------------------------------------

def get_supabase() -> Client:
    """
    Create the server-side Supabase client.

    SUPABASE_SERVER_KEY must be stored only in Streamlit Secrets.

    Do NOT expose this key in GitHub, frontend code, JavaScript, or
    browser-visible configuration.
    """

    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVER_KEY"]
    except KeyError as exc:
        raise RuntimeError(
            "Missing Supabase configuration. "
            "Add SUPABASE_URL and SUPABASE_SERVER_KEY "
            "to Streamlit Secrets."
        ) from exc

    if not isinstance(url, str) or not url.strip():
        raise RuntimeError(
            "SUPABASE_URL is empty or invalid."
        )

    if not isinstance(key, str) or not key.strip():
        raise RuntimeError(
            "SUPABASE_SERVER_KEY is empty or invalid."
        )

    return create_client(
        url.strip(),
        key.strip(),
    )


# ---------------------------------------------------------------------------
# RESPONSE NORMALIZATION
# ---------------------------------------------------------------------------

def _response_rows(
    response: Any,
) -> list[dict[str, Any]]:
    """
    Normalize Supabase response data.

    Current supabase-py responses expose `.data`, but this helper also
    accepts dictionary-like responses to avoid unnecessary AttributeErrors.
    """

    data = getattr(
        response,
        "data",
        None,
    )

    if data is None and isinstance(
        response,
        dict,
    ):
        data = response.get("data")

    if data is None:
        return []

    if not isinstance(data, list):
        raise RuntimeError(
            "Supabase returned an unexpected response format."
        )

    return [
        row
        for row in data
        if isinstance(row, dict)
    ]


# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------

def load_progress() -> dict[str, Any]:
    """
    Load durable state for the authenticated learner.

    Returns:
        {} when no record exists yet.
        Otherwise, the JSON object stored in learner_progress.progress.
    """

    client = get_supabase()
    user_id = get_user_id()

    response = (
        client
        .table("learner_progress")
        .select("progress")
        .eq(
            "user_id",
            user_id,
        )
        .limit(1)
        .execute()
    )

    rows = _response_rows(response)

    if not rows:
        return {}

    progress = rows[0].get(
        "progress",
        {},
    )

    if progress is None:
        return {}

    if not isinstance(progress, dict):
        raise RuntimeError(
            "Stored learner progress must be a JSON object."
        )

    return progress


# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------

def save_progress(
    progress: dict[str, Any],
) -> None:
    """
    Save durable state for the authenticated learner.

    The learner ID is always derived internally from the OIDC identity.
    """

    if not isinstance(
        progress,
        dict,
    ):
        raise TypeError(
            "Learner progress must be a dictionary."
        )

    client = get_supabase()
    user_id = get_user_id()

    payload = {
        "user_id": user_id,
        "progress": progress,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    (
        client
        .table("learner_progress")
        .upsert(
            payload,
            on_conflict="user_id",
        )
        .execute()
    )
