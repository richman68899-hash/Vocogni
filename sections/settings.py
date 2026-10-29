"""Settings page for the current Vocogni learning prototype.

Settings are saved through state.py's shared durable learner-state flow.
This page intentionally exposes only controls that the current app supports,
and describes prototype preferences honestly instead of implying features
that are not implemented yet.
"""
from __future__ import annotations

import re
from typing import Any

import streamlit as st
import styles
import onboarding
from legal_notices import render_legal_notices

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
        if widget_key not in st.session_state:
            st.session_state[widget_key] = valid_value
            continue

        current_value = st.session_state[widget_key]
        allowed_values = SETTING_OPTIONS.get(setting_key)
        if allowed_values is not None and current_value not in allowed_values:
            st.session_state[widget_key] = valid_value
            continue

        # Normalize malformed saved/widget values (notably custom hex colours),
        # while preserving valid choices already made in the current rerun.
        normalized = _safe_value(setting_key, current_value)
        if normalized != current_value:
            st.session_state[widget_key] = normalized


def _apply_values(values: dict[str, Any]) -> None:
    """Apply a preset/reset before widget construction on the next rerun."""
    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = dict(DEFAULT_SETTINGS)
        st.session_state.settings = settings

    updated = dict(settings)
    changed = False
    for setting_key, value in values.items():
        if setting_key in DEFAULT_SETTINGS:
            validated = _safe_value(setting_key, value)
            if updated.get(setting_key) != validated:
                changed = True
            updated[setting_key] = validated

    st.session_state.settings = updated
    for setting_key, widget_key in SETTING_WIDGET_KEYS.items():
        if setting_key in values:
            st.session_state[widget_key] = updated[setting_key]

    if changed:
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
    st.caption("Adjust the interface and learning support to suit your study preferences. Changes save automatically.")
    st.markdown(f"<div class='vc-muted'>{_current_summary(_current_widget_values(settings))}</div>", unsafe_allow_html=True)

    # Quick setups are just shortcuts over existing controls. Learners can
    # change any individual setting afterwards.
    with st.container(border=True):
        st.subheader("Quick setups")
        st.caption("Start with a preset, then fine-tune individual preferences.")

        preset_cols = st.columns(3, gap="medium")
        presets = [
            ("Focused study", "Reduced motion, no answer sounds, and one feedback summary at the end of a lesson."),
            ("Reading comfort", "Larger text, more line spacing, and less motion."),
            ("Gentle practice", "Immediate feedback, with available hints shown automatically."),
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

    # The first-run walkthrough is available again from Settings at any time.
    # It reuses the same saved completion flag and never resets learner progress.
    with st.container(border=True):
        st.subheader("Guided tour")
        tour_complete = onboarding.is_tutorial_complete(settings)
        if tour_complete:
            st.caption("You've completed the tour. Replay it whenever you need a refresher.")
        else:
            st.caption("Take a short, guided look around Learn, practice, progress, notes, and settings.")
        st.button(
            "Replay guided tour" if tour_complete else "Restart guided tour",
            key="settings_restart_guided_tour",
            type="primary",
            on_click=onboarding.start_tutorial,
            use_container_width=True,
        )

    # Keep decorative controls in a full-width panel rather than an overly tall
    # half-width column. Group the controls by what they change.
    with st.container(border=True):
        st.subheader("Appearance")
        st.caption("Personalize the typeface, colour mood, and shape of your workspace.")
        theme_col, style_col, accent_col = st.columns([1, 1, 1.05], gap="large")

        with theme_col:
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

        with style_col:
            st.selectbox(
                "Interface font",
                SETTING_OPTIONS["font_family"],
                key=SETTING_WIDGET_KEYS["font_family"],
                help="Changes the typeface throughout lessons, navigation, and settings.",
            )
            st.selectbox(
                "Background tone",
                SETTING_OPTIONS["background_tone"],
                key=SETTING_WIDGET_KEYS["background_tone"],
                help="Choose a neutral, warm paper-like, or cool blue-grey workspace.",
            )
            st.selectbox(
                "Corner style",
                SETTING_OPTIONS["corner_style"],
                key=SETTING_WIDGET_KEYS["corner_style"],
                help="Changes the shape of cards, inputs, and buttons across the app.",
            )

        with accent_col:
            st.toggle(
                "Use a custom accent colour",
                key=SETTING_WIDGET_KEYS["use_custom_accent"],
                help="Customize buttons, links, progress indicators, and active navigation.",
            )
            st.color_picker(
                "Accent colour",
                key=SETTING_WIDGET_KEYS["custom_accent_color"],
                disabled=not st.session_state[SETTING_WIDGET_KEYS["use_custom_accent"]],
                help="Low-contrast colours are adjusted automatically to keep controls readable.",
            )

        st.caption("Your choices apply across Vocogni and save automatically.")
        st.markdown("**Preview**")
        custom_enabled = bool(st.session_state[SETTING_WIDGET_KEYS["use_custom_accent"]])
        selected_accent = _safe_value(
            "custom_accent_color",
            st.session_state[SETTING_WIDGET_KEYS["custom_accent_color"]],
        )
        preview_css = styles.build_css({
            "appearance": st.session_state[SETTING_WIDGET_KEYS["appearance"]],
            "background_tone": st.session_state[SETTING_WIDGET_KEYS["background_tone"]],
            "use_custom_accent": custom_enabled,
            "custom_accent_color": selected_accent,
        })
        accent_match = re.search(r"--vc-accent: (#[0-9A-F]{6});", preview_css)
        text_match = re.search(r"--vc-on-accent: (#[0-9A-F]{6});", preview_css)
        preview_accent = accent_match.group(1) if accent_match else selected_accent
        preview_text = text_match.group(1) if text_match else "#FFFFFF"
        st.markdown(
            "<div class='vc-summary-box' style='border-left-color:"
            + preview_accent
            + ";'>"
            "<strong>Example lesson note</strong><br>"
            "Read the idea, solve a question, then apply it to a new problem.<br>"
            "<span style='display:inline-block;margin-top:.55rem;padding:.18rem .5rem;"
            "border-radius:5px;background:"
            + preview_accent
            + ";color:"
            + preview_text
            + ";font-size:.78rem;font-weight:600;'>Accent preview</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.subheader("Learning preferences")
        st.caption("Choose when to see feedback and when to use hints.")
        feedback_col, hint_col = st.columns(2, gap="large")
        with feedback_col:
            st.radio(
                "Feedback timing",
                SETTING_OPTIONS["feedback_timing"],
                key=SETTING_WIDGET_KEYS["feedback_timing"],
                help=(
                    "Immediate gives feedback after each question. "
                    "After submission shows a combined summary at the end of the lesson."
                ),
            )
        with hint_col:
            st.selectbox(
                "Hint assistance",
                SETTING_OPTIONS["difficulty"],
                format_func=lambda value: {
                    "Adaptive": "On request",
                    "Easy": "Automatic hints",
                    "Hard": "No hints",
                }.get(value, value),
                key=SETTING_WIDGET_KEYS["difficulty"],
                help=(
                    "On request reveals an authored hint only when you ask. "
                    "Automatic hints show authored support immediately. No hints hides it. "
                    "This changes assistance, not the underlying question bank."
                ),
            )
            difficulty = st.session_state[SETTING_WIDGET_KEYS["difficulty"]]
            if difficulty == "Easy":
                st.info("Authored hints appear automatically on supported questions.")
            elif difficulty == "Adaptive":
                st.caption("Hints stay hidden until you select Show hint on a supported question.")
            else:
                st.caption("Authored hints remain hidden for this setup.")

    focus_col, reading_col = st.columns(2, gap="large")

    with focus_col:
        with st.container(border=True):
            st.subheader("Focus & interaction")
            st.caption("Control motion and optional answer sounds.")
            st.toggle(
                "Motion and transitions",
                key=SETTING_WIDGET_KEYS["animations"],
                help="Turn this off to suppress the app's transitions and smooth scrolling.",
            )
            st.toggle(
                "Correct-answer sound",
                key=SETTING_WIDGET_KEYS["sound"],
                help="Plays a brief, warm bass-and-chime cue after a fully correct lesson answer. Off by default.",
            )
            st.toggle(
                "Incorrect-answer cue",
                key=SETTING_WIDGET_KEYS["wrong_answer_sound"],
                help="Plays a short descending bell cue after an incorrect lesson answer. Off by default.",
            )
            st.toggle(
                "Wrong-answer shake",
                key=SETTING_WIDGET_KEYS["answer_shake"],
                help="Adds a brief horizontal shake to incorrect-answer feedback. Off by default.",
            )
            if st.session_state[SETTING_WIDGET_KEYS["answer_shake"]]:
                st.warning(
                    "Motion warning: incorrect answers will briefly shake the feedback card. "
                    "This may be uncomfortable if you are sensitive to motion. "
                    "Keep it off if you experience discomfort; reduced-motion system settings disable the effect."
                )

    with reading_col:
        with st.container(border=True):
            st.subheader("Reading comfort")
            st.caption("Make lesson text easier to read without changing its content.")
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
            st.caption("These options change display and motion only, not lesson content. Typography, colour, and card shape are controlled above.")

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
        st.caption("Your preferences save automatically. A brief confirmation appears after a successful save; any save error stays visible in the sidebar.")

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

    st.divider()
    st.header("Terms, privacy & AI safety")
    st.caption("Read what the current prototype does, what learner data it uses, and the limits of its learning support.")
    render_legal_notices(st)
