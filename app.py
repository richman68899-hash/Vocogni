"""
app.py — VOCogni Version 1 entry point.

Run with:  streamlit run app.py

This file only handles page setup, the persistent sidebar, and routing to
the active section. All real logic lives in state.py / logic.py / data.py
and the actual UI for each of the five sections lives in sections/*.py.

Note on CSS ordering: build_css() is called *after* the active section has
rendered (not before), so that if the person just changed a Settings toggle
(e.g. Dark mode) during this same rerun, the new value is already in
st.session_state.settings by the time the stylesheet is built. A <style>
tag affects the whole page regardless of where in the script it was
emitted, so this does not delay anything visually — it just avoids the
toggle feeling like it takes an extra click to apply.
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

NAV_ITEMS = ["Profile", "Progress", "Browse", "Notes", "Settings"]

SECTION_RENDERERS = {
    "Profile": profile_section.render,
    "Progress": progress_section.render,
    "Browse": browse_section.render,
    "Notes": notes_section.render,
    "Settings": settings_section.render,
}


def _render_logo():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "vocogni_logo.png")
    st.sidebar.markdown("<div class='vc-logo-wrap'>", unsafe_allow_html=True)
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        # Spec section 20: fall back to clean text, never generate a replacement logo.
        st.sidebar.markdown(
            "<div class='vc-logo-text'>VOCogni</div>"
            "<div class='vc-logo-tag'>Understand \u2192 Solve \u2192 Apply \u2192 Advance</div>",
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def _render_nav():
    for item in NAV_ITEMS:
        active = st.session_state.nav == item
        if st.sidebar.button(
            item,
            key=f"nav_{item}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav = item
            st.rerun()

    profile_name = st.session_state.profile.get("name", "").strip()
    if profile_name:
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        st.sidebar.markdown(
            f"<span class='vc-muted'>Signed in as {html.escape(profile_name)}</span>",
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(page_title="VOCogni", page_icon="\U0001F393", layout="wide")

    state.init_session_state()

    _render_logo()
    _render_nav()

    renderer = SECTION_RENDERERS.get(st.session_state.nav, browse_section.render)
    renderer()

    st.markdown(styles.build_css(st.session_state.settings), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
