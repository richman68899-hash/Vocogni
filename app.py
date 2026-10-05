"""
app.py — VOCogni Version 1.1.0 entry point.

Run with:
    streamlit run app.py

This file handles:
- page setup
- Auth0 authentication
- persistent sidebar
- navigation
- routing to the active section

Application logic remains in:
- state.py
- logic.py
- data.py
- sections/*.py

Authentication:
- Auth0 handles user identity.
- Streamlit handles the authenticated session.
- Supabase stores persistent learner data.
"""

import html
import os

import streamlit as st

import state
import styles

from sections import browse as browse_section
from sections import notes as notes_section
from sections import profile as profile_section
from sections import progress as progress_section
from sections import settings as settings_section


# ============================================================
# NAVIGATION
# ============================================================

NAV_ITEMS = [
    "Profile",
    "Progress",
    "Browse",
    "Notes",
    "Settings",
]


SECTION_RENDERERS = {
    "Profile": profile_section.render,
    "Progress": progress_section.render,
    "Browse": browse_section.render,
    "Notes": notes_section.render,
    "Settings": settings_section.render,
}


# ============================================================
# AUTHENTICATION
# ============================================================

def _render_login() -> None:
    """
    Render the authentication entry screen.

    Auth0 handles the actual login/signup interface.
    Streamlit handles the OIDC callback and session.
    """

    st.title("Welcome to Vocogni")

    st.write(
        "Log in to save and restore your learning progress."
    )

    st.button(
        "Log in with Auth0",
        on_click=st.login,
        args=["auth0"],
        use_container_width=True,
    )

    # Do not render the application while unauthenticated.
    st.stop()


# ============================================================
# LOGO
# ============================================================

def _render_logo() -> None:

    logo_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "assets",
        "vocogni_logo.png",
    )

    st.sidebar.markdown(
        "<div class='vc-logo-wrap'>",
        unsafe_allow_html=True,
    )

    if os.path.exists(logo_path):

        st.sidebar.image(
            logo_path,
            use_container_width=True,
        )

    else:

        # Keep the original fallback behavior.
        st.sidebar.markdown(
            "<div class='vc-logo-text'>VOCogni</div>"
            "<div class='vc-logo-tag'>"
            "Understand → Solve → Apply → Advance"
            "</div>",
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# NAVIGATION
# ============================================================

def _render_nav() -> None:

    for item in NAV_ITEMS:

        active = (
            st.session_state.nav == item
        )

        if st.sidebar.button(
            item,
            key=f"nav_{item}",
            type=(
                "primary"
                if active
                else "secondary"
            ),
            use_container_width=True,
        ):

            st.session_state.nav = item
            st.rerun()

    # --------------------------------------------------------
    # Authenticated user identity
    # --------------------------------------------------------

    user_name = ""

    try:
        user_name = (
            st.user.get("name", "")
            or st.user.get("email", "")
            or ""
        )

    except Exception:
        user_name = ""

    # Fall back to the existing Vocogni profile.
    if not user_name:

        user_name = (
            st.session_state.profile
            .get("name", "")
            .strip()
        )

    if user_name:

        st.sidebar.markdown(
            "<hr>",
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            (
                "<span class='vc-muted'>"
                "Signed in as "
                f"{html.escape(str(user_name))}"
                "</span>"
            ),
            unsafe_allow_html=True,
        )


# ============================================================
# LOGOUT
# ============================================================

def _render_logout() -> None:
    """
    Save learner state and then end the authenticated session.
    """

    if not st.sidebar.button(
        "Log out",
        key="vocogni_logout",
        use_container_width=True,
    ):
        return

    # --------------------------------------------------------
    # Save before logout
    # --------------------------------------------------------

    try:
        state.persist_learner_state()

    except Exception as exc:

        # Do NOT silently discard unsaved learner progress.
        st.error(
            "Vocogni could not save your latest progress. "
            "You have not been logged out. "
            f"Error: {exc}"
        )

        return

    # --------------------------------------------------------
    # End Streamlit/Auth0 session
    # --------------------------------------------------------

    st.logout()


# ============================================================
# PERSISTENT LEARNER STATE
# ============================================================

def _load_persistent_state() -> None:
    """
    Load the authenticated learner's durable state.

    state.py owns the actual mapping between:
        Supabase → learner state
    """

    state.load_saved_learner_state()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # Must happen before other Streamlit page output.
    st.set_page_config(
        page_title="VOCogni",
        page_icon="🎓",
        layout="wide",
    )

    # ========================================================
    # AUTHENTICATION GATE
    # ========================================================

    if not st.user.is_logged_in:
        _render_login()

    # ========================================================
    # EXISTING VOCogni APPLICATION
    # ========================================================

    # Initialize temporary/session-level application state.
    state.init_session_state()

    # Restore durable learner state from Supabase.
    _load_persistent_state()

    # Persistent UI.
    _render_logo()
    _render_nav()
    _render_logout()

    # Route to the selected section.
    renderer = SECTION_RENDERERS.get(
        st.session_state.nav,
        browse_section.render,
    )

    renderer()

    # Apply current settings after the active section has rendered.
    st.markdown(
        styles.build_css(
            st.session_state.settings
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
