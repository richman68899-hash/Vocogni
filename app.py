def main():

    st.set_page_config(
        page_title="VOCogni",
        page_icon="🎓",
        layout="wide",
    )

    if not _render_authentication():
        st.stop()

    state.init_session_state()

    # load persistent learner state

    _render_logo()
    _render_nav()

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
