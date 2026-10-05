"""
persistence.py — VOCogni Version 1.1.0 persistence layer.

Responsibilities:
- identify the currently authenticated learner
- connect to Supabase PostgreSQL
- load durable learner progress
- save durable learner progress

Authentication is handled by:
    Auth0 → Streamlit OIDC → st.user

This module does NOT:
- manage passwords
- perform login/signup
- store Supabase Auth sessions
- manage access/refresh tokens
- handle UI state

The database stores durable learner state only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions


# ============================================================
# SUPABASE CLIENT
# ============================================================

def get_supabase() -> Client:
    """
    Create the server-side Supabase client.

    The Supabase server key must exist only in Streamlit Secrets.
    It must never be placed in GitHub or exposed to the browser.
    """

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVER_KEY"],
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


# ============================================================
# AUTHENTICATED USER IDENTITY
# ============================================================

def get_user_id() -> str:
    """
    Return the current learner's stable Auth0/OIDC subject ID.

    Auth0 authenticates the learner.
    Streamlit exposes the resulting identity through st.user.
    """

    if not st.user.is_logged_in:
        raise RuntimeError(
            "No authenticated Vocogni user is available."
        )

    user_id = st.user.get("sub")

    if not user_id:
        raise RuntimeError(
            "The authenticated user has no OIDC subject ID."
        )

    return str(user_id)


# ============================================================
# LOAD PROGRESS
# ============================================================

def load_progress() -> dict[str, Any]:
    """
    Load durable progress for the currently authenticated learner.

    Returns:
        The learner's stored progress dictionary.
        Returns an empty dictionary when no record exists yet.
    """

    client = get_supabase()
    user_id = get_user_id()

    response = (
        client
        .table("learner_progress")
        .select("progress")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return {}

    progress = response.data[0].get(
        "progress",
        {},
    )

    if not isinstance(progress, dict):
        raise RuntimeError(
            "Stored learner progress has an invalid format."
        )

    return progress


# ============================================================
# SAVE PROGRESS
# ============================================================

def save_progress(
    progress: dict[str, Any],
) -> None:
    """
    Persist durable progress for the currently authenticated learner.

    The learner ID is derived internally from st.user.
    Callers cannot choose another user's ID.
    """

    if not isinstance(progress, dict):
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

    client.table(
        "learner_progress"
    ).upsert(
        payload
    ).execute()


# ============================================================
# OPTIONAL: ENSURE A LEARNER RECORD EXISTS
# ============================================================

def ensure_progress_record() -> None:
    """
    Ensure that the authenticated learner has a progress row.

    This is safe to call after login.
    If the learner already has a row, it is left unchanged.
    """

    client = get_supabase()
    user_id = get_user_id()

    response = (
        client
        .table("learner_progress")
        .select("user_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return

    client.table(
        "learner_progress"
    ).insert(
        {
            "user_id": user_id,
            "progress": {},
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }
    ).execute()
