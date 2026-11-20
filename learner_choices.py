"""Learner-facing controls for optional personalisation and AI data sharing.

These are feature preferences, not legal consent records and not guardian consent.
"""
from __future__ import annotations

from typing import Any
import os

DEVELOPER_SANDBOX_ENV = "VOCogni_DEVELOPER_SANDBOX"
_TRUE_VALUES = {"1", "true", "yes", "on"}

def developer_sandbox_enabled(environ: Any = None) -> bool:
    """Explicit server-side switch for developer-only experimentation."""
    values = os.environ if environ is None else environ
    return str(values.get(DEVELOPER_SANDBOX_ENV, "")).strip().casefold() in _TRUE_VALUES




CHOICE_WIDGET_KEYS = {
    "personalized_progress_recommendations": "choice_personalized_progress_recommendations",
    "ai_share_learning_summary": "choice_ai_share_learning_summary",
    "ai_share_recent_chat_history": "choice_ai_share_recent_chat_history",
}

CHOICE_DETAILS = {
    "personalized_progress_recommendations": {
        "label": "Use my saved learning results for personalised recommendations",
        "description": (
            "When on, the Progress page uses recorded practice, diagnostics, and "
            "teaching-support history to show Learning Intelligence recommendations, "
            "skill trends, and an intervention timeline. When off, that personalised "
            "recommendation panel is hidden. Basic account saving, course feedback, "
            "and ordinary progress records still work."
        ),
    },
    "ai_share_learning_summary": {
        "label": "Include my saved learning summary in external AI tutoring",
        "description": (
            "When on, an external AI tutoring request may include a limited summary "
            "of learning preferences, overall/course practice accuracy, and recent "
            "mistake tags. It is sent only when the operator has enabled external AI "
            "and you separately enable AI tutoring for the current session."
        ),
    },
    "ai_share_recent_chat_history": {
        "label": "Include previous AI tutor messages in future requests",
        "description": (
            "When on, up to eight messages from earlier external-AI tutoring turns "
            "may accompany your next request. When off, only your current message is "
            "sent, plus the saved learning summary if you separately enabled it."
        ),
    },
}


def choice_enabled(settings: Any, key: str) -> bool:
    """Fail closed: only an explicit boolean True enables an optional data use."""
    if key not in CHOICE_WIDGET_KEYS or not isinstance(settings, dict):
        return False
    return settings.get(key) is True


def _persist_choice(choice_key: str) -> None:
    """Persist one feature preference via the existing learner-state autosave."""
    if choice_key not in CHOICE_WIDGET_KEYS:
        return

    import streamlit as st
    import state

    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}

    widget_key = CHOICE_WIDGET_KEYS[choice_key]
    selected = st.session_state.get(widget_key) is True
    if settings.get(choice_key) is selected:
        return

    updated = dict(settings)
    updated[choice_key] = selected
    st.session_state.settings = updated
    state.mark_persistent_dirty()


def _complete_first_run_choices(skip_optional: bool = False) -> None:
    """Record that the preference screen was reviewed; never create consent."""
    import streamlit as st
    import state

    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}

    updated = dict(settings)
    if skip_optional:
        for choice_key, widget_key in CHOICE_WIDGET_KEYS.items():
            updated[choice_key] = False
            # This callback runs before Streamlit rebuilds the widgets.
            st.session_state[widget_key] = False

    updated["learning_data_choices_reviewed"] = True
    st.session_state.settings = updated
    state.mark_persistent_dirty()


def render_choice_controls(st: Any, settings: Any) -> None:
    """Render three independent, opt-in feature choices with no preselected switches."""
    current = settings if isinstance(settings, dict) else {}
    for key, widget_key in CHOICE_WIDGET_KEYS.items():
        if widget_key not in st.session_state:
            st.session_state[widget_key] = choice_enabled(current, key)

        details = CHOICE_DETAILS[key]
        st.toggle(
            details["label"],
            key=widget_key,
            on_change=_persist_choice,
            args=(key,),
        )
        st.caption(details["description"])


def render_first_run_choices(st: Any) -> bool:
    """Render the one-time choices screen; return True while it is shown."""
    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}
        st.session_state.settings = settings

    if developer_sandbox_enabled():
        # Enable only personalised Progress; external AI context sharing stays off.
        updated = dict(settings)
        updated["personalized_progress_recommendations"] = True
        updated["ai_share_learning_summary"] = False
        updated["ai_share_recent_chat_history"] = False
        updated["learning_data_choices_reviewed"] = True
        if updated != settings:
            import state
            st.session_state.settings = updated
            state.mark_persistent_dirty()
        return False

    if settings.get("learning_data_choices_reviewed") is True:
        return False

    st.markdown("### Your learning and data choices")
    with st.container(border=True):
        st.caption(
            "Nothing below is switched on automatically. These are separate "
            "feature preferences, and you can change them later in Settings."
        )
        render_choice_controls(st, settings)

        st.markdown("**What Vocogni saves to provide your account**")
        st.write(
            "Vocogni currently saves account information and learning records such "
            "as course progress, practice results, notes, and settings so that your "
            "work can be restored and the app can show your progress. The optional "
            "switches above do not turn off this core account storage."
        )

        st.warning(
            "These switches record feature preferences only. They do not ask for "
            "or prove parent/guardian consent. The current prototype does not yet "
            "verify or record guardian consent, so this screen does not make "
            "real child accounts ready for release."
        )

        skip_col, continue_col = st.columns(2, gap="small")
        with skip_col:
            st.button(
                "Keep optional features off",
                key="learning_choices_skip_optional",
                on_click=_complete_first_run_choices,
                args=(True,),
                use_container_width=True,
            )
        with continue_col:
            st.button(
                "Continue with my choices",
                key="learning_choices_continue",
                type="primary",
                on_click=_complete_first_run_choices,
                args=(False,),
                use_container_width=True,
            )
    return True


def render_settings_controls(st: Any) -> None:
    """Render the same real preference controls in Settings for later changes."""
    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}

    with st.container(border=True):
        st.subheader("Learning and data choices")
        st.caption(
            "These switches control the optional features described below. "
            "They are not a general data-consent form."
        )
        render_choice_controls(st, settings)
        st.caption(
            "Your current message is always sent to the configured external AI "
            "provider when you use external AI tutoring. The two AI-sharing switches "
            "separately control whether saved learning context and previous AI tutor "
            "messages are added."
        )
        st.warning(
            "These preferences do not replace verified parent/guardian permission. "
            "The prototype's guardian-consent process remains unimplemented."
        )
