"""
app.py — VOCogni Version 1.1.0 entry point.

Run with: streamlit run app.py

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

from persistence import (
    get_current_user,
    sign_in,
    sign_up,
    sign_out,
)

from sections import browse as browse_section
from sections import notes as notes_section
from sections import profile as profile_section
from sections import progress as progress_section
from sections import settings as settings_section


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


def _render_authentication() -> bool:
    """
    Render the login/signup screen.

    Returns True when the user is authenticated.
    Returns False when the authentication screen
    is being displayed.
    """

    user = get_current_user()

    # User is already authenticated.
    if user is not None:
        return True

    st.title("Welcome to Vocogni")

    st.write(
        "Log in to save and restore your learning progress."
    )

    login_tab, signup_tab = st.tabs(
        [
            "Log in",
            "Create account",
        ]
    )

    # -----------------------------
    # LOGIN
    # -----------------------------

    with login_tab:

        with st.form("vocogni_login_form"):

            email = st.text_input(
                "Email",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Log in"
            )

        if submitted:

            if not email.strip():

                st.error(
                    "Enter your email address."
                )

            elif not password:

                st.error(
                    "Enter your password."
                )

            else:

                try:

                    sign_in(
                        email,
                        password,
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Login failed: {exc}"
                    )

    # -----------------------------
    # SIGN UP
    # -----------------------------

    with signup_tab:

        with st.form("vocogni_signup_form"):

            email = st.text_input(
                "Email",
                key="signup_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
            )

            confirmation = st.text_input(
                "Confirm password",
                type="password",
                key="signup_confirmation",
            )

            submitted = st.form_submit_button(
                "Create account"
            )

        if submitted:

            if not email.strip():

                st.error(
                    "Enter your email address."
                )

            elif not password:

                st.error(
                    "Enter a password."
                )

            elif password != confirmation:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 8:

                st.error(
                    "Password must be at least 8 characters."
                )

            else:

                try:

                    response = sign_up(
                        email,
                        password,
                    )

                    # Email confirmation enabled.
                    if response.session is None:

                        st.success(
                            "Account created. "
                            "Check your email to confirm your account."
                        )

                    else:

                        st.success(
                            "Account created."
                        )

                        st.rerun()

                except Exception as exc:

                    st.error(
                        f"Sign-up failed: {exc}"
                    )

    return False


def _render_logo():

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


def _render_nav():

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

    profile_name = (
        st.session_state.profile
        .get("name", "")
        .strip()
    )

    if profile_name:

        st.sidebar.markdown(
            "<hr>",
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            (
                "<span class='vc-muted'>"
                f"Signed in as "
                f"{html.escape(profile_name)}"
                "</span>"
            ),
            unsafe_allow_html=True,
        )


def _render_logout():

    if st.sidebar.button(
        "Log out",
        key="vocogni_logout",
        use_container_width=True,
    ):

        try:

            # Save learner state if the persistence
            # integration has added this function.
            persist_function = getattr(
                state,
                "persist_learner_state",
                None,
            )

            if persist_function is not None:
                persist_function()

        finally:

            sign_out()

        st.rerun()


def _load_persistent_state():

    """
    Load durable learner state after authentication.

    This uses the integration function if it exists.
    """

    load_function = getattr(
        state,
        "load_saved_learner_state",
        None,
    )

    if load_function is not None:
        load_function()


def main():

    st.set_page_config(
        page_title="VOCogni",
        page_icon="🎓",
        layout="wide",
    )

    # =================================================
    # AUTHENTICATION GATE
    # =================================================

    if not _render_authentication():
        st.stop()

    # =================================================
    # VOCogNI APPLICATION
    # =================================================

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


if __name__ == "__main__":
    main()
