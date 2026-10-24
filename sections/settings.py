"""Settings page for the current Vocogni learning prototype.

Settings are saved through state.py's shared durable learner-state flow.
This page intentionally exposes only controls that the current app supports,
and describes prototype preferences honestly instead of implying features
that are not implemented yet.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from version import APP_VERSION
import state
from settings_model import (
    DEFAULT_SETTINGS,
    PRESETS,
    SETTING_OPTIONS,
    SETTING_WIDGET_KEYS,
    current_summary as _current_summary,
    safe_value as _safe_value,
    settings_changed as _settings_changed,
)


def _ensure_widget_state(settings: dict[str, Any]) -> None:
    """Initialize widget keys from saved preferences without overriding edits."""
    for setting_key, widget_key in SETTING_WIDGET_KEYS.items():
        valid_value = _safe_value(
            setting_key,
            settings.get(setting_key, DEFAULT_SETTINGS[setting_key]),
        )
        if widget_key not in st.session_state or st.session_state[widget_key] not in (
            SETTING_OPTIONS.get(setting_key, [False, True])
        ):
            st.session_state[widget_key] = valid_value


def _apply_values(values: dict[str, Any]) -> None:
    """Apply a preset/reset before widget construction on the next rerun."""
    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = dict(DEFAULT_SETTINGS)
        st.session_state.settings = settings

    updated = dict(settings)
    for setting_key, value in values.items():
        if setting_key in DEFAULT_SETTINGS:
            updated[setting_key] = _safe_value(setting_key, value)

    st.session_state.settings = updated
    for setting_key, widget_key in SETTING_WIDGET_KEYS.items():
        if setting_key in values:
            st.session_state[widget_key] = updated[setting_key]

    state.mark_persistent_dirty()


def _apply_preset(name: str) -> None:
    """Apply one named learning setup to the existing preferences."""
    if name == "Balanced defaults":
        _apply_values(DEFAULT_SETTINGS)
    elif name in PRESETS:
        _apply_values(PRESETS[name])


def _restore_defaults() -> None:
    """Restore every setting to its original default."""
    _apply_values(DEFAULT_SETTINGS)


def _current_widget_values(settings: dict[str, Any]) -> dict[str, Any]:
    """Read the latest widget values for accurate summaries before syncing."""
    current = dict(settings)
    for setting_key, widget_key in SETTING_WIDGET_KEYS.items():
        current[setting_key] = _safe_value(setting_key, st.session_state[widget_key])
    # One visible motion control maps to the two legacy settings keys, keeping
    # older saved records compatible without presenting duplicate switches.
    current["reduced_motion"] = not current.get("animations", True)
    return current


def render() -> None:
    """Render the Settings page with clear groupings and auto-save behavior."""
    settings = st.session_state.settings
    _ensure_widget_state(settings)

    st.title("Settings")
    st.caption("Set up how Vocogni looks and how lessons respond. Changes apply immediately and save automatically.")
    st.markdown(f"<div class='vc-muted'>{_current_summary(_current_widget_values(settings))}</div>", unsafe_allow_html=True)

    # Quick setups are just shortcuts over existing controls. Learners can
    # change any individual setting afterwards.
    with st.container(border=True):
        st.subheader("Quick setups")
        st.caption("Choose a starting point, then adjust any setting below.")

        preset_cols = st.columns(3, gap="medium")
        presets = [
            ("Focused study", "Less motion and sound, with feedback grouped at the end."),
            ("Reading comfort", "Larger text, more spacing, and reduced motion."),
            ("Gentle practice", "Shows authored hints where available and keeps feedback immediate."),
        ]
        for column, (name, description) in zip(preset_cols, presets):
            with column:
                st.markdown(f"**{name}**")
                st.caption(description)
                st.button(
                    "Apply setup",
                    key=f"apply_settings_preset_{name.lower().replace(' ', '_')}",
                    use_container_width=True,
                    on_click=_apply_preset,
                    args=(name,),
                )

    appearance_col, learning_col = st.columns(2, gap="large")

    with appearance_col:
        with st.container(border=True):
            st.subheader("Appearance")
            st.caption("Choose the visual theme and the standard text scale.")
            st.radio(
                "Theme",
                SETTING_OPTIONS["appearance"],
                horizontal=True,
                key=SETTING_WIDGET_KEYS["appearance"],
            )
            st.radio(
                "Text size",
                SETTING_OPTIONS["text_size"],
                horizontal=True,
                key=SETTING_WIDGET_KEYS["text_size"],
            )
            st.markdown("**Preview**")
            st.markdown(
                "<div class='vc-summary-box'>"
                "<strong>Example lesson note</strong><br>"
                "Read the idea, solve a question, then apply it to a new problem."
                "</div>",
                unsafe_allow_html=True,
            )

    with learning_col:
        with st.container(border=True):
            st.subheader("Learning preferences")
            st.caption("Control feedback timing and the available hint preference.")
            st.radio(
                "Feedback timing",
                SETTING_OPTIONS["feedback_timing"],
                key=SETTING_WIDGET_KEYS["feedback_timing"],
                help=(
                    "Immediate gives feedback after each question. "
                    "After submission shows a combined summary at the end of the lesson."
                ),
            )
            st.selectbox(
                "Difficulty preference",
                SETTING_OPTIONS["difficulty"],
                key=SETTING_WIDGET_KEYS["difficulty"],
                help=(
                    "Easy reveals authored hints when a question provides one. "
                    "Adaptive, Medium, and Hard are saved preferences; they do not "
                    "currently regenerate or reorder the authored question bank."
                ),
            )
            difficulty = st.session_state[SETTING_WIDGET_KEYS["difficulty"]]
            if difficulty == "Easy":
                st.info("Hint support is shown only on questions that have an authored hint.")
            else:
                st.caption("Questions and progression continue to follow the course's authored learning path.")

    focus_col, reading_col = st.columns(2, gap="large")

    with focus_col:
        with st.container(border=True):
            st.subheader("Focus & interaction")
            st.caption("Reduce extra effects and choose whether correct answers play a sound.")
            st.toggle(
                "Motion and transitions",
                key=SETTING_WIDGET_KEYS["animations"],
                help="Turn this off to suppress the app's transitions and smooth scrolling.",
            )
            st.toggle(
                "Correct-answer sound",
                key=SETTING_WIDGET_KEYS["sound"],
                help="Plays a short tone after a correct answer. Browser audio settings may still block it.",
            )

    with reading_col:
        with st.container(border=True):
            st.subheader("Reading comfort")
            st.caption("Adjust text display without changing lesson content.")
            st.toggle(
                "Larger text",
                key=SETTING_WIDGET_KEYS["larger_text"],
                help="Raises the base text size beyond the selected text-size setting.",
            )
            st.toggle(
                "High-readability spacing",
                key=SETTING_WIDGET_KEYS["high_readability"],
                help="Increases line spacing to make longer text blocks easier to track.",
            )
            st.caption("These options change display and motion only, not lesson content.")

    st.divider()
    reset_col, info_col = st.columns([1, 3], gap="medium")
    with reset_col:
        st.button(
            "Restore defaults",
            key="restore_settings_defaults",
            on_click=_restore_defaults,
            use_container_width=True,
        )
    with info_col:
        st.caption("Settings are saved through your existing Vocogni learner record. Save status remains visible in the sidebar.")

    new_values = {
        setting_key: _safe_value(setting_key, st.session_state[widget_key])
        for setting_key, widget_key in SETTING_WIDGET_KEYS.items()
    }
    # The old schema had separate animation/reduced-motion switches that
    # implemented the same CSS behavior. Keep both persisted keys aligned.
    new_values["reduced_motion"] = not new_values["animations"]
    if _settings_changed(settings, new_values):
        settings.update(new_values)
        state.mark_persistent_dirty()

    st.divider()
    st.caption(f"Vocogni v{APP_VERSION}")
