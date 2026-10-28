"""Trust, privacy, and AI-safety policy surfaces for the Vocogni prototype.

The policy files are the source of truth. They are drafts until the service
operator, contact route, consent mechanisms, and legal review are complete.
"""
from __future__ import annotations

from pathlib import Path



_POLICY_FILES = {
    "terms": ("terms-of-service.md", "Terms of Service"),
    "privacy": ("privacy-notice.md", "Privacy Notice"),
    "ai_safety": ("ai-use-and-safety.md", "AI Use & Safety"),
}


def load_policy(key: str) -> str:
    """Load one policy document from the repository's docs folder."""
    if key not in _POLICY_FILES:
        raise KeyError(f"Unknown policy document: {key}")

    filename, _title = _POLICY_FILES[key]
    path = Path(__file__).resolve().parents[1] / "docs" / filename
    return path.read_text(encoding="utf-8")


def _render_policy_tabs() -> None:
    import streamlit as st

    tabs = st.tabs(["Terms of service", "Privacy notice", "AI use & safety"])
    for tab, key in zip(tabs, ("terms", "privacy", "ai_safety")):
        with tab:
            try:
                st.markdown(load_policy(key))
            except OSError:
                st.error("This policy document could not be loaded. Please try again later.")


def render_login_disclosure() -> None:
    """Expose policy drafts before sign-in without pretending to capture consent."""
    with st.expander("Terms, privacy and AI safety (draft)", expanded=False):
        st.warning(
            "Vocogni is a development prototype. These are working policy drafts, "
            "not a finalized legal agreement or proof of compliance. The current app "
            "does not verify guardian consent or provide complete privacy-request and "
            "safety-reporting workflows."
        )
        _render_policy_tabs()


def render() -> None:
    """Render the in-product Trust & Safety page."""
    import streamlit as st

    st.title("Trust & safety")
    st.markdown(
        "<p class='vc-page-intro'>How Vocogni works, what data it uses, and the limits "
        "learners should understand before using the prototype.</p>",
        unsafe_allow_html=True,
    )
    st.warning(
        "**Development status — not cleared for public release.** These policy documents "
        "are drafts, not legal advice or a compliance certification. The operator and "
        "monitored contact details are not yet configured; guardian-consent recording, "
        "privacy-rights handling, and a monitored safety-reporting process are incomplete. "
        "Do not enter highly sensitive information."
    )

    _render_policy_tabs()

    st.divider()
    st.caption(
        "Policy owner, contact details, retention periods, provider configuration, "
        "age-appropriate controls, and required consent processes must be verified "
        "before public launch."
    )
