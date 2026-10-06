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

Responsibilities:
- identify the authenticated learner
- connect to Supabase
- load durable learner state
- save durable learner state

This module does NOT:
- manage passwords
- perform login/signup
- use Supabase Auth sessions
- store OAuth access/refresh tokens
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from postgrest.exceptions import APIError
from supabase import Client, create_client


TABLE_NAME = "learner_progress"


# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------

def mark_persistent_dirty() -> None:
    """
    Mark durable learner state as changed.

    This does not immediately contact Supabase.
    The save is flushed later during the same Streamlit run.
    """

    st.session_state["_persistent_dirty"] = True
    st.session_state["_persistent_save_status"] = "pending"
    st.session_state["_persistent_save_error"] = None

def has_pending_persistence() -> bool:
    """
    Return True when durable learner state has unsaved changes.
    """

    return bool(
        st.session_state.get(
            "_persistent_dirty",
            False,
        )
    )

def _get_user_claims() -> dict[str, Any]:
    """
    Safely convert Streamlit's authenticated OIDC user into a dictionary.
    """

    user = st.user

    try:
        claims = user.to_dict()
    except AttributeError:
        try:
            claims = dict(user)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "VOCogni could not read the authenticated OIDC user."
            ) from exc

    if not isinstance(claims, dict):
        raise RuntimeError(
            "VOCogni received an invalid authenticated user object."
        )

    return claims


def _is_logged_in() -> bool:
    """
    Return True when Streamlit has an authenticated user.
    """

    try:
        return bool(st.user.is_logged_in)
    except AttributeError:
        claims = _get_user_claims()
        return bool(claims.get("sub"))


def get_user_id() -> str:
    """
    Return the stable OIDC subject ID for the current learner.

    Example:
        google-oauth2|123456789...

    The email address is deliberately NOT used as the database identity.
    """

    if not _is_logged_in():
        raise RuntimeError(
            "No authenticated Vocogni user is available."
        )

    claims = _get_user_claims()

    user_id = claims.get("sub")

    if not user_id:
        raise RuntimeError(
            "The authenticated user has no OIDC 'sub' claim."
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

    Legacy fallback:
        SUPABASE_KEY

    The server key must never be exposed in GitHub or browser-side code.
    """

    if "SUPABASE_URL" not in st.secrets:
        raise RuntimeError(
            "Missing SUPABASE_URL in Streamlit Secrets."
        )

    supabase_url = st.secrets["SUPABASE_URL"]

    if "SUPABASE_SERVER_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_SERVER_KEY"]

    elif "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]

    else:
        raise RuntimeError(
            "Missing Supabase API key. "
            "Add SUPABASE_SERVER_KEY to Streamlit Secrets."
        )

    if not isinstance(supabase_url, str) or not supabase_url.strip():
        raise RuntimeError(
            "SUPABASE_URL is empty or invalid."
        )

    if not isinstance(supabase_key, str) or not supabase_key.strip():
        raise RuntimeError(
            "The Supabase API key is empty or invalid."
        )

    return create_client(
        supabase_url.strip(),
        supabase_key.strip(),
    )


# ---------------------------------------------------------------------------
# RESPONSE HELPERS
# ---------------------------------------------------------------------------

def _response_rows(
    response: Any,
) -> list[dict[str, Any]]:
    """
    Normalize Supabase response data.
    """

    rows = getattr(
        response,
        "data",
        None,
    )

    if rows is None and isinstance(response, dict):
        rows = response.get("data")

    if rows is None:
        return []

    if not isinstance(rows, list):
        raise RuntimeError(
            "Supabase returned an unexpected response format."
        )

    return [
        row
        for row in rows
        if isinstance(row, dict)
    ]


def _format_database_error(
    error: Exception,
) -> str:
    """
    Convert a Supabase/PostgREST error into a useful, non-secret message.
    """

    message = str(error).strip()

    lowered = message.lower()

    if "uuid" in lowered:
        return (
            "Supabase rejected the learner ID because the "
            "learner_progress.user_id column is probably still UUID. "
            "Change that column to TEXT using the VOCogni SQL migration."
        )

    if (
        "permission denied" in lowered
        or "42501" in lowered
    ):
        return (
            "Supabase denied access to learner_progress. "
            "Grant SELECT/INSERT/UPDATE/DELETE to service_role "
            "and expose the table through the Data API."
        )

    if (
        "relation" in lowered
        and "does not exist" in lowered
    ):
        return (
            "The Supabase table public.learner_progress does not exist."
        )

    if "column" in lowered and "does not exist" in lowered:
        return (
            "The learner_progress table is missing a required column."
        )

    if "schema cache" in lowered:
        return (
            "PostgREST has stale schema information. "
            "Reload the schema with: NOTIFY pgrst, 'reload schema';"
        )

    # Keep the actual PostgREST message because this is already running
    # server-side and does not contain our secret keys.
    return f"Supabase database error: {message}"


# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------

def load_progress() -> dict[str, Any]:
    """
    Load durable learner state.

    Returns:
        {} when this learner has no record yet.
    """

    user_id = get_user_id()
    client = get_supabase()

    try:
        response = (
            client
            .table(TABLE_NAME)
            .select("progress")
            .eq(
                "user_id",
                user_id,
            )
            .limit(1)
            .execute()
        )

    except APIError as exc:
        raise RuntimeError(
            _format_database_error(exc)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"VOCogni could not contact Supabase: {exc}"
        ) from exc

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
    Save durable learner state for the authenticated learner.
    """

    if not isinstance(progress, dict):
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

    try:
        (
            client
            .table(TABLE_NAME)
            .upsert(
                payload,
                on_conflict="user_id",
            )
            .execute()
        )

    except APIError as exc:
        raise RuntimeError(
            _format_database_error(exc)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"VOCogni could not save learner data: {exc}"
        ) from exc

def flush_persistent_save() -> bool:
    """
    Save durable learner state when a meaningful change has been made.

    Returns:
        True if there was no pending save or the save succeeded.
        False if the save failed.
    """

    if not has_pending_persistence():
        return True

    st.session_state["_persistent_save_status"] = "saving"
    st.session_state["_persistent_save_error"] = None

    try:
        persist_learner_state()

    except Exception as exc:
        st.session_state["_persistent_save_status"] = "error"
        st.session_state["_persistent_save_error"] = str(exc)

        return False

    st.session_state["_persistent_dirty"] = False
    st.session_state["_persistent_save_status"] = "saved"
    st.session_state["_persistent_save_error"] = None
    st.session_state["_persistent_last_saved_at"] = (
        datetime.now(timezone.utc).isoformat()
    )
    st.session_state["_persistent_save_count"] += 1

    return True
