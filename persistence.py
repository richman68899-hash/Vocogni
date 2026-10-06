"""
persistence.py — VOCogni Version 1.2.0 persistence layer.

Architecture:

    Google
       ↓
    Auth0
       ↓
    Streamlit OIDC
       ↓
    st.user["sub"]
       ↓
    persistence.py
       ↓
    Supabase PostgreSQL

Responsibilities:
- identify the authenticated learner
- create the server-side Supabase client
- load durable learner state
- save durable learner state
- verify successful database writes
- provide safe, useful database errors

This module does NOT:
- manage passwords
- perform login/signup
- manage Streamlit session state
- decide when autosave occurs
- mark learner state dirty
- flush autosaves
- store OAuth access/refresh tokens

IMPORTANT:
Autosave state management belongs in state.py.

    state.py
        mark_persistent_dirty()
        has_pending_persistence()
        flush_persistent_save()

    persistence.py
        get_user_id()
        load_progress()
        save_progress()
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from postgrest.exceptions import APIError
from supabase import Client, create_client


TABLE_NAME = "learner_progress"


# ============================================================================
# AUTHENTICATION
# ============================================================================

def _get_user_claims() -> dict[str, Any]:
    """
    Safely convert Streamlit's authenticated OIDC user into a dictionary.

    Streamlit exposes st.user as a dict-like object containing claims from
    the configured OIDC provider.
    """

    user = st.user

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
    Return the stable OIDC subject identifier for the current learner.

    Example:
        google-oauth2|123456789...

    This value is stored in learner_progress.user_id.

    The learner's email address is intentionally NOT used as the
    database identity.
    """

    if not _is_logged_in():
        raise RuntimeError(
            "No authenticated VOCogNI user is available."
        )

    claims = _get_user_claims()

    user_id = claims.get("sub")

    if not user_id:
        raise RuntimeError(
            "The authenticated user has no OIDC 'sub' claim."
        )

    return str(user_id)


# ============================================================================
# SUPABASE CLIENT
# ============================================================================

def get_supabase() -> Client:
    """
    Create the server-side Supabase client.

    Primary configuration:
        SUPABASE_URL
        SUPABASE_SERVER_KEY

    Temporary compatibility fallback:
        SUPABASE_KEY

    SUPABASE_SERVER_KEY must contain an elevated server-only Supabase
    secret key and must exist only in Streamlit Secrets.

    It must never be:
    - committed to GitHub
    - placed in frontend/browser code
    - displayed to users
    - printed in logs
    """

    # ------------------------------------------------------------------------
    # Supabase URL
    # ------------------------------------------------------------------------

    if "SUPABASE_URL" not in st.secrets:
        raise RuntimeError(
            "Missing SUPABASE_URL in Streamlit Secrets."
        )

    supabase_url = st.secrets["SUPABASE_URL"]

    # ------------------------------------------------------------------------
    # Preferred server-side key
    # ------------------------------------------------------------------------

    if "SUPABASE_SERVER_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_SERVER_KEY"]

    # ------------------------------------------------------------------------
    # Compatibility with the older VOCogNI configuration
    # ------------------------------------------------------------------------

    elif "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]

    else:
        raise RuntimeError(
            "Missing Supabase server key. "
            "Add SUPABASE_SERVER_KEY to Streamlit Secrets."
        )

    # ------------------------------------------------------------------------
    # Validate configuration
    # ------------------------------------------------------------------------

    if (
        not isinstance(supabase_url, str)
        or not supabase_url.strip()
    ):
        raise RuntimeError(
            "SUPABASE_URL is empty or invalid."
        )

    if (
        not isinstance(supabase_key, str)
        or not supabase_key.strip()
    ):
        raise RuntimeError(
            "The Supabase API key is empty or invalid."
        )

    supabase_key = supabase_key.strip()

    # Warn if the wrong type of new-format key was supplied.
    # The application will continue, allowing the actual API to report
    # the precise failure if necessary.
    if supabase_key.startswith("sb_publishable_"):
        st.warning(
            "VOCogNI is using a Supabase publishable key for server-side "
            "persistence. Use an sb_secret_ key in SUPABASE_SERVER_KEY "
            "for the production server configuration."
        )

    # ------------------------------------------------------------------------
    # Create the client
    # ------------------------------------------------------------------------

    return create_client(
        supabase_url.strip(),
        supabase_key,
    )


# ============================================================================
# RESPONSE NORMALIZATION
# ============================================================================

def _response_rows(
    response: Any,
) -> list[dict[str, Any]]:
    """
    Normalize data returned by Supabase/PostgREST.

    Current supabase-py responses expose `.data`.
    """

    rows = getattr(
        response,
        "data",
        None,
    )

    # Defensive compatibility with dictionary-like responses.
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


# ============================================================================
# DATABASE ERROR HANDLING
# ============================================================================

def _format_database_error(
    error: Exception,
) -> str:
    """
    Convert a Supabase/PostgREST exception into a useful message without
    exposing credentials or other secrets.
    """

    message = str(error).strip()
    lowered = message.lower()

    # ------------------------------------------------------------------------
    # UUID → TEXT migration problem
    # ------------------------------------------------------------------------

    if "uuid" in lowered:
        return (
            "Supabase rejected the learner ID because "
            "learner_progress.user_id may still be UUID. "
            "VOCogNI v1.2.0 expects user_id to be TEXT so it can "
            "store the Auth0/OIDC sub value."
        )

    # ------------------------------------------------------------------------
    # PostgreSQL permission problem
    # ------------------------------------------------------------------------

    if (
        "permission denied" in lowered
        or "42501" in lowered
    ):
        return (
            "Supabase denied access to learner_progress. "
            "Check the service_role table grants and Data API exposure."
        )

    # ------------------------------------------------------------------------
    # Table does not exist
    # ------------------------------------------------------------------------

    if (
        "relation" in lowered
        and "does not exist" in lowered
    ):
        return (
            "The Supabase table public.learner_progress does not exist."
        )

    # ------------------------------------------------------------------------
    # Missing column
    # ------------------------------------------------------------------------

    if (
        "column" in lowered
        and "does not exist" in lowered
    ):
        return (
            "The learner_progress table is missing a required column."
        )

    # ------------------------------------------------------------------------
    # PostgREST schema cache
    # ------------------------------------------------------------------------

    if "schema cache" in lowered:
        return (
            "PostgREST has stale schema information. "
            "Reload the schema with: "
            "NOTIFY pgrst, 'reload schema';"
        )

    # ------------------------------------------------------------------------
    # Constraint / conflict problem
    # ------------------------------------------------------------------------

    if (
        "duplicate key" in lowered
        or "unique constraint" in lowered
        or "conflict" in lowered
    ):
        return (
            "Supabase rejected the learner save because of a database "
            "uniqueness or conflict constraint. Check that user_id is "
            "the primary key or has a UNIQUE constraint."
        )

    # ------------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------------

    return f"Supabase database error: {message}"


# ============================================================================
# LOAD
# ============================================================================

def load_progress() -> dict[str, Any]:
    """
    Load durable learner state for the currently authenticated learner.

    Returns:
        {} if no learner record exists yet.
        Otherwise, the JSON object stored in learner_progress.progress.

    Identity is always derived internally from the authenticated OIDC
    subject. The caller cannot supply an arbitrary learner ID.
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
            f"VOCogNI could not contact Supabase: {exc}"
        ) from exc

    rows = _response_rows(response)

    # No database record yet.
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


# ============================================================================
# SAVE
# ============================================================================

def save_progress(
    progress: dict[str, Any],
) -> None:
    """
    Persist durable learner state for the currently authenticated learner.

    Uses upsert() so:
    - first save creates the learner record
    - later saves update the same learner record

    The resulting database row is explicitly selected after the upsert
    so VOCogNI can verify that the write actually returned a record.

    Supabase documents chaining .select() after upsert() to return the
    resulting row. 
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
        response = (
            client
            .table(TABLE_NAME)
            .upsert(
                payload,
                on_conflict="user_id",
            )
            .select(
                "user_id, updated_at"
            )
            .execute()
        )

    except APIError as exc:
        raise RuntimeError(
            _format_database_error(exc)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"VOCogNI could not save learner data: {exc}"
        ) from exc

    rows = _response_rows(response)

    if not rows:
        raise RuntimeError(
            "Supabase accepted the save request but returned "
            "no learner record. The write could not be verified."
        )

    returned_user_id = rows[0].get("user_id")

    if str(returned_user_id) != user_id:
        raise RuntimeError(
            "Supabase returned a learner record belonging to a "
            "different identity. Save verification failed."
        )
