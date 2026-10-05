"""
app.py — VOCogni Version 1.1.0 entry point.

Run with:
    streamlit run app.py

This file handles:
- page setup
- authentication gate
- persistent sidebar
- routing to the active section

Application logic remains in:
- state.py
- logic.py
- data.py
- sections/*.py
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
    Render the login screen for unauthenticated users.

    Authentication is handled by Streamlit's native OIDC
    integration with Auth0.
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

    # Prefer the authenticated identity from Auth0.
    # Fall back to the existing profile name if available.
    user_name = ""

    try:
        user_name = (
            st.user.get("name", "")
            or st.user.get("email", "")
            or ""
        )
    except Exception:
        user_name = ""

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

    if st.sidebar.button(
        "Log out",
        key="vocogni_logout",
        use_container_width=True,
    ):

        # Save learner state before ending the
        # current authenticated session.
        persist_function = getattr(
            state,
            "persist_learner_state",
            None,
        )

        if persist_function is not None:

            try:
                persist_function()

            except Exception as exc:
                st.warning(
                    "Your session was logged out, "
                    f"but progress could not be saved: {exc}"
                )

        # Streamlit handles the authentication
        # cookie and OIDC logout.
        st.logout()


# ============================================================
# PERSISTENT LEARNER STATE
# ============================================================

def _load_persistent_state() -> None:
    """
    Load durable learner state once after authentication.

    The actual implementation lives in state.py.
    """

    load_function = getattr(
        state,
        "load_saved_learner_state",
        None,
    )

    if load_function is not None:
        load_function()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

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

    state.init_session_state()

    _load_persistent_state()

    _render_logo()

    _render_nav()

    _render_logout()

    renderer = SECTION_RENDERERS.get(
        st.session_state.nav,
        browse_section.render,
    )

    renderer()

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
