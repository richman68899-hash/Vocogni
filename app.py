"""
app.py — Vocogni application entry point.

Streamlit/Auth0/Supabase remain the application foundation. The optional
LLM-powered Study Guide is rendered by vocogni_ai.py and is isolated from
learner-state persistence.
"""
from __future__ import annotations

import html
import os

import streamlit as st

import state
import styles
import onboarding
from vocogni_ai import render_assistant
from legal_notices import render_legal_notices

from sections import browse as browse_section
from sections import notes as notes_section
from sections import profile as profile_section
from sections import progress as progress_section
from sections import settings as settings_section


NAV_ITEMS = [
    ("Profile", "Profile"),
    ("Progress", "Progress"),
    ("Learn", "Browse"),
    ("Notes", "Notes"),
    ("Settings", "Settings"),
]

SECTION_RENDERERS = {
    "Profile": profile_section.render,
    "Progress": progress_section.render,
    "Browse": browse_section.render,
    "Notes": notes_section.render,
    "Settings": settings_section.render,
}


def _render_login() -> None:
    """Render the authentication entry screen."""
    _left, hero, _right = st.columns([1, 2, 1], gap="small")
    with hero:
        st.markdown(
            "<div class='vc-login-hero'>"
            "<h1>Learning that moves you forward.</h1>"
            "<p class='vc-page-intro'>Sign in to continue learning, revisit your notes, and pick up where you left off.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.button(
            "Continue to Vocogni",
            type="primary",
            on_click=st.login,
            args=["auth0"],
            use_container_width=True,
        )

    st.divider()
    st.markdown("#### Terms, privacy & AI safety")
    st.caption("Review these prototype notices before signing in.")
    render_legal_notices(st, compact=True)
    st.stop()


def _render_logo() -> None:
    """Render a compact, accessible Vocogni wordmark in the sidebar."""
    logo_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "vocogni_logo.png",
    )
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=188)
    else:
        st.sidebar.markdown(
            "<div class='vc-logo-wrap'>"
            "<div class='vc-logo-row'><span class='vc-logo-mark'>V</span>"
            "<div class='vc-logo-text'>Vocogni</div></div>"
            "</div>",
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
        "<div class='vc-sidebar-tagline'>Understand <span>·</span> Practise <span>·</span> Apply</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<hr class='vc-sidebar-divider'>", unsafe_allow_html=True)


def _render_nav() -> None:
    """Render the persistent sidebar navigation."""
    for label, route in NAV_ITEMS:
        active = st.session_state.nav == route
        if st.sidebar.button(
            label,
            key=f"nav_{route}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav = route

    user_name = ""
    email_hint = ""
    try:
        user_name = str(st.user.get("name", "") or "").strip()
        email_hint = str(st.user.get("email", "") or "").strip()
    except Exception:
        user_name = ""
        email_hint = ""

    if not user_name:
        profile = st.session_state.get("profile", {})
        if isinstance(profile, dict):
            user_name = str(profile.get("name", "") or "").strip()

    if user_name or email_hint:
        identity = user_name or email_hint
        initial = html.escape(identity[:1].upper() or "A", quote=True)
        hover_label = html.escape(
            f"Signed in as {user_name}" if user_name else "Signed-in account",
            quote=True,
        )
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        st.sidebar.markdown(
            "<div style='display:flex;align-items:center;gap:.6rem;padding:.2rem 0;'>"
            f"<span title='{hover_label}' aria-label='{hover_label}' "
            "style='display:inline-flex;align-items:center;justify-content:center;"
            "width:2rem;height:2rem;border-radius:50%;border:1px solid var(--vc-border,#d8e1dc);"
            "font-weight:700;cursor:default;'>"
            f"{initial}</span><span class='vc-muted'>Account</span></div>",
            unsafe_allow_html=True,
        )


def _render_persistence_status() -> None:
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    state.render_save_status()


def _render_logout() -> None:
    """Save pending learner state before ending the authenticated session."""
    if not st.sidebar.button(
        "Log out",
        key="vocogni_logout",
        use_container_width=True,
    ):
        return

    try:
        state.persist_learner_state()
    except Exception as exc:
        st.error(
            "Vocogni could not save your latest progress. "
            "You have not been logged out. "
            f"Error: {exc}"
        )
        return

    st.logout()


def _load_persistent_state() -> None:
    state.load_saved_learner_state()


def main() -> None:
    """Run the authenticated Vocogni application."""
    st.set_page_config(
        page_title="Vocogni",
        page_icon="🎓",
        layout="wide",
    )

    if not st.user.is_logged_in:
        st.markdown(styles.build_css({}), unsafe_allow_html=True)
        _render_login()

    state.init_session_state()
    _load_persistent_state()
    onboarding.render_tutorial(st)

    _render_logo()
    _render_nav()
    _render_logout()

    renderer = SECTION_RENDERERS.get(
        st.session_state.nav,
        browse_section.render,
    )
    renderer()

    # The Study Guide uses the current session's learner context but does not
    # mutate or persist learner state. External AI calls require session opt-in.
    if st.session_state.nav == "Browse":
        render_assistant(
            st,
            st.session_state.profile,
            st.session_state.progress,
            settings=st.session_state.settings,
            notes=st.session_state.notes,
            milestones=st.session_state.milestones,
        )

    previous_save_count = int(st.session_state.get("_persistent_save_count", 0) or 0)
    state.flush_persistent_save()
    current_save_count = int(st.session_state.get("_persistent_save_count", 0) or 0)
    if current_save_count > previous_save_count:
        st.toast("Changes saved", icon="✅")

    _render_persistence_status()
    st.markdown(
        styles.build_css(st.session_state.settings),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
