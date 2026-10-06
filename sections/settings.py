"""
sections/settings.py — Settings.

VOCogni Version 1.2.0

Settings apply immediately.

Persistence behavior:
- Settings widgets are intentionally outside a form.
- Streamlit reruns when a setting changes.
- The current values are compared with the durable settings stored in
  st.session_state.
- If a meaningful setting changed, the durable state is updated and
  state.mark_persistent_dirty() is called.
- app.py performs the actual Supabase save through
  state.flush_persistent_save().

No separate "Save Settings" button is required.

The settings control:
- appearance
- text size
- feedback timing
- difficulty
- animations
- sound
- reduced motion
- larger text
- high readability
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import state


# ===========================================================================
# HELPERS
# ===========================================================================

def _safe_index(
    options: list[str],
    value: Any,
    fallback: int = 0,
) -> int:
    """
    Return the index of value in options.

    Falls back safely when an older persisted setting contains an invalid
    or removed option.
    """

    try:
        return options.index(value)

    except (ValueError, TypeError):
        return fallback


def _settings_changed(
    settings: dict[str, Any],
    new_values: dict[str, Any],
) -> bool:
    """
    Return True when at least one durable setting actually changed.
    """

    for key, new_value in new_values.items():

        if settings.get(key) != new_value:
            return True

    return False


# ===========================================================================
# MAIN RENDER
# ===========================================================================

def render() -> None:
    """
    Render the settings page.

    The widgets themselves trigger Streamlit reruns when changed.
    At the end of the function we synchronize the current widget values
    into the durable settings dictionary and mark the state dirty only
    when something actually changed.
    """

    st.markdown(
        "<h2>Settings</h2>",
        unsafe_allow_html=True,
    )

    settings = st.session_state.settings

    # =======================================================================
    # APPEARANCE
    # =======================================================================

    st.markdown(
        "<h3>Appearance</h3>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:

        appearance_options = [
            "Light",
            "Dark",
        ]

        appearance = st.radio(
            "Theme",
            appearance_options,
            index=_safe_index(
                appearance_options,
                settings.get(
                    "appearance",
                    "Light",
                ),
            ),
            horizontal=True,
        )

    with c2:

        text_size_options = [
            "Small",
            "Medium",
            "Large",
        ]

        text_size = st.radio(
            "Text size",
            text_size_options,
            index=_safe_index(
                text_size_options,
                settings.get(
                    "text_size",
                    "Medium",
                ),
                fallback=1,
            ),
            horizontal=True,
        )

    # =======================================================================
    # LEARNING EXPERIENCE
    # =======================================================================

    st.markdown(
        "<h3 style='margin-top:1.2rem;'>"
        "Learning experience"
        "</h3>",
        unsafe_allow_html=True,
    )

    c3, c4 = st.columns(2)

    with c3:

        feedback_options = [
            "Immediate",
            "After submission",
        ]

        feedback_timing = st.radio(
            "Feedback",
            feedback_options,
            index=_safe_index(
                feedback_options,
                settings.get(
                    "feedback_timing",
                    "Immediate",
                ),
            ),
            horizontal=True,
            help=(
                "Immediate shows correctness right after each "
                "question. After submission shows a combined "
                "summary at the end of the lesson."
            ),
        )

    with c4:

        difficulty_options = [
            "Adaptive",
            "Easy",
            "Medium",
            "Hard",
        ]

        difficulty = st.radio(
            "Difficulty",
            difficulty_options,
            index=_safe_index(
                difficulty_options,
                settings.get(
                    "difficulty",
                    "Adaptive",
                ),
            ),
            horizontal=True,
            help=(
                "Prototype preference. Easy also shows a hint "
                "on numeric questions."
            ),
        )

    # =======================================================================
    # INTERACTION
    # =======================================================================

    st.markdown(
        "<h3 style='margin-top:1.2rem;'>"
        "Interaction"
        "</h3>",
        unsafe_allow_html=True,
    )

    c5, c6 = st.columns(2)

    with c5:

        animations = st.toggle(
            "Animations",
            value=bool(
                settings.get(
                    "animations",
                    True,
                )
            ),
            help=(
                "Enables animated transitions and visual effects."
            ),
        )

    with c6:

        sound = st.toggle(
            "Sound",
            value=bool(
                settings.get(
                    "sound",
                    True,
                )
            ),
            help=(
                "Plays a short tone on a correct answer."
            ),
        )

    # =======================================================================
    # ACCESSIBILITY
    # =======================================================================

    st.markdown(
        "<h3 style='margin-top:1.2rem;'>"
        "Accessibility"
        "</h3>",
        unsafe_allow_html=True,
    )

    reduced_motion = st.checkbox(
        "Reduced motion",
        value=bool(
            settings.get(
                "reduced_motion",
                False,
            )
        ),
        help=(
            "Turns off transitions and animated effects "
            "throughout the app."
        ),
    )

    larger_text = st.checkbox(
        "Larger text",
        value=bool(
            settings.get(
                "larger_text",
                False,
            )
        ),
        help=(
            "Increases the base text size beyond the "
            "Text size option above."
        ),
    )

    high_readability = st.checkbox(
        "High readability mode",
        value=bool(
            settings.get(
                "high_readability",
                False,
            )
        ),
        help=(
            "Increases line spacing to make longer text "
            "easier to read."
        ),
    )

    st.markdown(
        "<p class='vc-muted' style='margin-top:0.6rem;'>"
        "These accessibility options only adjust spacing, motion, "
        "and text size. VOCogni does not make medical claims about "
        "ADHD or neurodivergence."
        "</p>",
        unsafe_allow_html=True,
    )

    # =======================================================================
    # SYNCHRONIZE DURABLE SETTINGS
    # =======================================================================
    #
    # Widgets are outside a form, so changing one causes Streamlit to rerun.
    # The values returned above therefore represent the latest committed
    # widget values for this run.
    #
    # We compare them against the existing durable settings first.
    # This prevents unnecessary database writes.
    # =======================================================================

    new_values = {
        "appearance": appearance,
        "text_size": text_size,
        "feedback_timing": feedback_timing,
        "difficulty": difficulty,
        "animations": animations,
        "sound": sound,
        "reduced_motion": reduced_motion,
        "larger_text": larger_text,
        "high_readability": high_readability,
    }

    changed = _settings_changed(
        settings,
        new_values,
    )

    if changed:

        # Update the durable learner state.
        settings.update(
            new_values
        )

        # Tell the central autosave system that durable learner data
        # has changed.
        state.mark_persistent_dirty()
