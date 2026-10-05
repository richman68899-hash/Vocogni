"""
persistence.py — VOCogni Version 1.1.0 persistence layer.

Authentication:
    Google
       ↓
    Auth0
       ↓
    Streamlit OIDC
       ↓
    st.user

Persistence:
    st.user["sub"]
       ↓
    Supabase PostgreSQL

This module:
- identifies the authenticated learner
- creates the server-side Supabase client
- loads learner data
- saves learner data

This module does NOT:
- manage passwords
- perform login/signup
- use Supabase Auth sessions
- store OAuth tokens
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client


# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------

def _is_logged_in() -> bool:
    """
    Safely determine whether the current Streamlit user is authenticated.
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
    Return the authenticated learner's stable OIDC subject ID.

    Example:
        google-oauth2|123456789...

    Do NOT use the email address as the database identity.
    """

    if not _is_logged_in():
        raise RuntimeError(
            "No authenticated Vocogni user is available."
        )

    user = st.user

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
            "The authenticated user has no OIDC subject (sub) claim."
        )

    return str(user_id)


# ---------------------------------------------------------------------------
# SUPABASE CLIENT
# ---------------------------------------------------------------------------

def get_supabase() -> Client:
    """
    Create the server-side Supabase client.

    Preferred secret:
        SUPABASE_SERVER_KEY

    Temporary compatibility fallback:
        SUPABASE_KEY

    The fallback exists because older Vocogni configuration used
    SUPABASE_KEY. The recommended production configuration is still
    SUPABASE_SERVER_KEY containing an sb_secret_... key.
    """

    # ---------------------------------------------------------------
    # Supabase URL
    # ---------------------------------------------------------------

    try:
        supabase_url = st.secrets["SUPABASE_URL"]
    except KeyError as exc:
        raise RuntimeError(
            "Missing SUPABASE_URL in Streamlit Secrets. "
            "Add your Supabase project URL."
        ) from exc

    # ---------------------------------------------------------------
    # Preferred server key
    # ---------------------------------------------------------------

    if "SUPABASE_SERVER_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_SERVER_KEY"]

    # ---------------------------------------------------------------
    # Backward compatibility with the old configuration
    # ---------------------------------------------------------------

    elif "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]

        st.warning(
            "VOCogni is using the legacy SUPABASE_KEY setting. "
            "For the final configuration, replace it with a "
            "server-only SUPABASE_SERVER_KEY (sb_secret_...)."
        )

    else:
        raise RuntimeError(
            "Missing Supabase API key in Streamlit Secrets. "
            "Add SUPABASE_SERVER_KEY = \"sb_secret_...\"."
        )

    # ---------------------------------------------------------------
    # Validate values
    # ---------------------------------------------------------------

    if not isinstance(
        supabase_url,
        str,
    ) or not supabase_url.strip():
        raise RuntimeError(
            "SUPABASE_URL is empty or invalid."
        )

    if not isinstance(
        supabase_key,
        str,
    ) or not supabase_key.strip():
        raise RuntimeError(
            "The Supabase API key is empty or invalid."
        )

    # ---------------------------------------------------------------
    # Create client
    # ---------------------------------------------------------------

    return create_client(
        supabase_url.strip(),
        supabase_key.strip(),
    )


# ---------------------------------------------------------------------------
# RESPONSE NORMALIZATION
# ---------------------------------------------------------------------------

def _response_rows(
    response: Any,
) -> list[dict[str, Any]]:
    """
    Normalize Supabase response data.
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

    if not isinstance(
        data,
        list,
    ):
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
    Load durable learner state from Supabase.

    Returns:
        {} if this learner does not yet have a database record.
    """

    user_id = get_user_id()
    client = get_supabase()

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

    if not isinstance(
        progress,
        dict,
    ):
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
    Save durable learner state to Supabase.
    """

    if not isinstance(
        progress,
        dict,
    ):
        raise TypeError(
            "Learner progress must be a dictionary."
        )

    user_id = get_user_id()
    client = get_supabase()

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
