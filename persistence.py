"""
persistence.py — Vocogni Version 1.2.0 persistence layer.

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
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import streamlit as st


TABLE_NAME = "learner_progress"

LOCAL_DEVELOPER_MODE_ENV = "VOCogni_LOCAL_DEVELOPER_MODE"
LOCAL_DEVELOPER_USER_ID = "local-developer"
LOCAL_DEVELOPER_DATA_DIR = Path(__file__).resolve().parent / ".vocogni_dev"


def local_developer_mode_enabled() -> bool:
    """True only when the dedicated local entry point enabled the sandbox."""
    return os.environ.get(LOCAL_DEVELOPER_MODE_ENV, "").strip().casefold() in {
        "1", "true", "yes", "on"
    }


def _is_postgrest_api_error(error: Exception) -> bool:
    """Identify PostgREST API errors without importing its SDK in local mode."""
    try:
        from postgrest.exceptions import APIError
    except Exception:
        return False
    return isinstance(error, APIError)


def _local_developer_data_path() -> Path:
    return LOCAL_DEVELOPER_DATA_DIR / "learner_progress.json"


def _load_local_progress_record() -> dict[str, Any]:
    """Read the developer's isolated JSON file; never contact a remote service."""
    path = _local_developer_data_path()
    if not path.exists():
        return {"progress": {}, "updated_at": None, "exists": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "The local Vocogni data file could not be read. It was left unchanged."
        ) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("progress"), dict):
        raise RuntimeError(
            "The local Vocogni data file has an invalid format. It was left unchanged."
        )
    revision = payload.get("updated_at")
    if revision is not None and not isinstance(revision, str):
        raise RuntimeError("The local Vocogni data revision is invalid.")
    return {"progress": payload["progress"], "updated_at": revision, "exists": True}


def _save_local_progress(
    progress: dict[str, Any],
    *,
    expected_updated_at: str | None,
    record_exists: bool,
) -> str:
    """Atomically save to the ignored local workspace with revision checks."""
    current = _load_local_progress_record()
    if record_exists:
        if not current["exists"] or current["updated_at"] != expected_updated_at:
            raise ConcurrentProgressUpdateError(
                "The local workspace changed in another session. Reload it before saving."
            )
    elif current["exists"]:
        raise ConcurrentProgressUpdateError(
            "A local workspace record was created in another session. Reload it before saving."
        )

    revision = datetime.now(timezone.utc).isoformat()
    payload = {
        "user_id": LOCAL_DEVELOPER_USER_ID,
        "progress": progress,
        "updated_at": revision,
    }
    path = _local_developer_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix="learner_progress.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, ensure_ascii=False, indent=2, allow_nan=False)
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    except (OSError, TypeError, ValueError) as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise RuntimeError("Vocogni could not save the local developer workspace.") from exc
    return revision




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
            "Vocogni could not read the authenticated OIDC user."
        ) from exc

    if not isinstance(claims, dict):
        raise RuntimeError(
            "Vocogni received an invalid authenticated user object."
        )

    return claims


def _is_logged_in() -> bool:
    """
    Return True when Streamlit has an authenticated user.
    """

    if local_developer_mode_enabled():
        return True

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

    if local_developer_mode_enabled():
        return LOCAL_DEVELOPER_USER_ID

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

def get_supabase() -> Any:
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

    if local_developer_mode_enabled():
        raise RuntimeError(
            "Supabase is disabled in Local Developer Mode. The workspace uses a local JSON file."
        )

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

    # Import the hosted database SDK only when the hosted persistence path is used.
    # Local Developer Mode uses JSON storage and must not load Supabase/cryptography.
    try:
        from supabase import create_client
    except Exception as exc:
        raise RuntimeError(
            "The Supabase SDK could not be loaded. Hosted persistence requires its "
            "native cryptography dependencies to be permitted by this Windows "
            "device's application-control policy."
        ) from exc

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

def load_progress_record() -> dict[str, Any]:
    """Load a learner row and its revision for optimistic concurrency checks."""
    if local_developer_mode_enabled():
        return _load_local_progress_record()

    user_id = get_user_id()
    client = get_supabase()

    try:
        response = (
            client
            .table(TABLE_NAME)
            .select("progress, updated_at")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        if _is_postgrest_api_error(exc):
            raise RuntimeError(_format_database_error(exc)) from exc
        raise RuntimeError(f"VOCogNI could not contact Supabase: {exc}") from exc

    rows = _response_rows(response)
    if not rows:
        return {"progress": {}, "updated_at": None, "exists": False}

    row = rows[0]
    progress = row.get("progress", {})
    if progress is None:
        progress = {}
    if not isinstance(progress, dict):
        raise RuntimeError("Stored learner progress must be a JSON object.")

    return {
        "progress": progress,
        "updated_at": row.get("updated_at"),
        "exists": True,
    }


def load_progress() -> dict[str, Any]:
    """Backward-compatible progress-only loader."""
    return load_progress_record()["progress"]

# ============================================================================
# SAVE
# ============================================================================

class ConcurrentProgressUpdateError(RuntimeError):
    """Raised when another session changed the learner row after it was loaded."""


def save_progress(
    progress: dict[str, Any],
    *,
    expected_updated_at: str | None = None,
    record_exists: bool = False,
) -> str:
    """Save only if the learner row still has the revision this session loaded.

    Existing rows use an atomic conditional UPDATE. A first save uses INSERT;
    a competing first save is reported as a concurrency conflict, not upserted
    over the row that another session just created.
    """
    if not isinstance(progress, dict):
        raise TypeError("Learner progress must be a dictionary.")

    if local_developer_mode_enabled():
        return _save_local_progress(
            progress,
            expected_updated_at=expected_updated_at,
            record_exists=record_exists,
        )

    user_id = get_user_id()
    client = get_supabase()
    payload = {
        "user_id": user_id,
        "progress": progress,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        query = client.table(TABLE_NAME)
        if record_exists:
            query = query.update(payload).eq("user_id", user_id)
            if expected_updated_at is None:
                query = query.is_("updated_at", "null")
            else:
                query = query.eq("updated_at", expected_updated_at)
        else:
            query = query.insert(payload)

        response = query.select("user_id, updated_at").execute()

    except Exception as exc:
        if not _is_postgrest_api_error(exc):
            raise RuntimeError(f"VOCogNI could not save learner data: {exc}") from exc
        message = str(exc).casefold()
        code = str(getattr(exc, "code", "") or "")
        if not record_exists and (code == "23505" or "23505" in message
                                  or "duplicate key" in message
                                  or "unique constraint" in message):
            raise ConcurrentProgressUpdateError(
                "A learner record was created in another session after this session loaded. "
                "Reload the latest saved data before continuing."
            ) from exc
        raise RuntimeError(_format_database_error(exc)) from exc

    rows = _response_rows(response)
    if not rows:
        if record_exists:
            raise ConcurrentProgressUpdateError(
                "Learner data changed in another session after this session loaded. "
                "Reload the latest saved data before continuing."
            )
        raise RuntimeError(
            "Supabase accepted the save request but returned no learner record. "
            "The write could not be verified."
        )

    returned_user_id = rows[0].get("user_id")
    if str(returned_user_id) != user_id:
        raise RuntimeError(
            "Supabase returned a learner record belonging to a different identity. "
            "Save verification failed."
        )

    updated_at = rows[0].get("updated_at")
    if not isinstance(updated_at, str) or not updated_at:
        raise RuntimeError(
            "Supabase saved the learner record but did not return its revision timestamp."
        )
    return updated_at
