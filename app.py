"""
app.py — VOCogni Version 1.2.0 entry point.

Run with:
    streamlit run app.py

This file handles:
- page setup
- Auth0 authentication
- persistent sidebar
- navigation
- routing to the active section
- end-of-run durable-state autosave

Application logic remains in:
- state.py
- logic.py
- data.py
- sections/*.py

Authentication:
- Auth0 handles user identity.
- Streamlit handles the authenticated OIDC session.
- Supabase stores persistent learner data.

Persistence:
- state.py owns session state and autosave coordination.
- persistence.py owns the Supabase database operation.
- Durable state is saved after meaningful learner-state mutations.
- Logout performs a final safety save.
"""

from __future__ import annotations

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
    """
    Render the VOCogni logo in the sidebar.
    """

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

        # Preserve the original fallback behavior.
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
    """
    Render the persistent sidebar navigation.

    IMPORTANT:
    Do not call st.rerun() manually here.

    Streamlit automatically reruns after button interaction. Allowing
    the current run to continue means the end-of-run autosave can flush
    any pending learner-state changes before the next run begins.
    """

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

            # Do NOT call st.rerun().
            #
            # The button interaction already causes Streamlit to rerun.
            # Continuing this run allows autosave to execute at the end.

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

    # Fall back to the existing VOCogni profile.
    if not user_name:

        profile = st.session_state.get(
            "profile",
            {},
        )

        if isinstance(profile, dict):

            user_name = (
                str(
                    profile.get(
                        "name",
                        "",
                    )
                ).strip()
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
# PERSISTENCE STATUS
# ============================================================

def _render_persistence_status() -> None:
    """
    Render the learner's current save status.

    This is intentionally placed below the navigation and identity so
    the learner can see whether their latest meaningful change has been
    saved.
    """

    st.sidebar.markdown(
        "<hr>",
        unsafe_allow_html=True,
    )

    state.render_save_status()


# ============================================================
# LOGOUT
# ============================================================

def _render_logout() -> None:
    """
    Perform a final safety save and then end the authenticated session.

    Normal learner-state persistence happens automatically through
    state.flush_persistent_save(). This final save exists as a safety
    checkpoint before logout.
    """

    if not st.sidebar.button(
        "Log out",
        key="vocogni_logout",
        use_container_width=True,
    ):
        return

    # --------------------------------------------------------
    # Final safety save
    # --------------------------------------------------------

    try:

        state.persist_learner_state()

    except Exception as exc:

        # Never silently discard the learner's latest changes.
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

    state.py owns the mapping between:
        Supabase → learner state
    """

    state.load_saved_learner_state()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """
    Main VOCogni application entry point.
    """

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
    # SESSION INITIALIZATION
    # ========================================================

    state.init_session_state()

    # ========================================================
    # RESTORE DURABLE LEARNER STATE
    # ========================================================

    _load_persistent_state()

    # ========================================================
    # PERSISTENT SIDEBAR
    # ========================================================

    _render_logo()
    _render_nav()
    _render_logout()

    # ========================================================
    # ROUTE TO ACTIVE SECTION
    # ========================================================

    renderer = SECTION_RENDERERS.get(
        st.session_state.nav,
        browse_section.render,
    )

    renderer()

    # ========================================================
    # V1.2.0 AUTOSAVE
    # ========================================================
    #
    # Section code is responsible for marking meaningful durable
    # mutations with:
    #
    #     state.mark_persistent_dirty()
    #
    # This single flush then performs at most one persistence
    # operation for the current Streamlit run.
    #
    # Navigation/search-only interactions that do not mark the state
    # dirty cause no database write.
    # ========================================================

    state.flush_persistent_save()

    # ========================================================
    # SAVE STATUS
    # ========================================================
    #
    # Render AFTER flush so the learner sees the result of the
    # current save attempt rather than the state from before it.
    # ========================================================

    _render_persistence_status()

    # ========================================================
    # APPLY CURRENT SETTINGS
    # ========================================================

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
