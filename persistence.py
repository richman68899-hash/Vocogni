from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client


def get_supabase() -> Client:
    """
    Create a Supabase client and restore the authenticated
    user's session when one exists.
    """

    client = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )

    access_token = st.session_state.get(
        "supabase_access_token"
    )

    refresh_token = st.session_state.get(
        "supabase_refresh_token"
    )

    if access_token and refresh_token:
        try:
            client.auth.set_session(
                access_token,
                refresh_token,
            )
        except Exception:
            # The stored session may have expired or become invalid.
            clear_auth_state()

    return client


def store_session(session: Any) -> None:
    """Store the authenticated user's session temporarily."""

    st.session_state["supabase_access_token"] = (
        session.access_token
    )

    st.session_state["supabase_refresh_token"] = (
        session.refresh_token
    )

    st.session_state["supabase_user_id"] = (
        session.user.id
    )

    st.session_state["supabase_user_email"] = (
        session.user.email
    )


def clear_auth_state() -> None:
    """Remove all temporary authentication state."""

    for key in (
        "supabase_access_token",
        "supabase_refresh_token",
        "supabase_user_id",
        "supabase_user_email",
        "learner_state_loaded",
    ):
        st.session_state.pop(key, None)


def sign_up(
    email: str,
    password: str,
):
    """Create a new Supabase Auth account."""

    client = get_supabase()

    response = client.auth.sign_up(
        {
            "email": email.strip(),
            "password": password,
        }
    )

    if response.user is None:
        raise RuntimeError(
            "Account creation failed."
        )

    if response.session is not None:
        store_session(response.session)

    return response


def sign_in(
    email: str,
    password: str,
):
    """Sign in using email and password."""

    client = get_supabase()

    response = client.auth.sign_in_with_password(
        {
            "email": email.strip(),
            "password": password,
        }
    )

    if (
        response.user is None
        or response.session is None
    ):
        raise RuntimeError(
            "Login failed."
        )

    store_session(response.session)

    return response


def get_current_user():
    """
    Validate the current authenticated user.

    Returns:
        Supabase user object, or None.
    """

    access_token = st.session_state.get(
        "supabase_access_token"
    )

    refresh_token = st.session_state.get(
        "supabase_refresh_token"
    )

    if not access_token or not refresh_token:
        return None

    try:
        client = get_supabase()

        response = client.auth.get_user(
            access_token
        )

        return response.user

    except Exception:
        clear_auth_state()
        return None


def sign_out() -> None:
    """Sign out the current local session."""

    try:
        client = get_supabase()

        client.auth.sign_out(
            {"scope": "local"}
        )

    finally:
        clear_auth_state()


def load_progress(
    user_id: str,
) -> dict[str, Any]:
    """
    Load persistent learner progress.

    RLS ensures that the authenticated user can
    only access their own row.
    """

    client = get_supabase()

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
        return {}

    return progress


def save_progress(
    user_id: str,
    progress: dict[str, Any],
) -> None:
    """
    Persist durable learner progress.
    """

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
        .upsert(payload)
        .execute()
    )
