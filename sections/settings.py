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
    AI_PREFERENCE_DEFAULTS,
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


def _select_settings_section(section: str) -> None:
    """Switch the visible Settings category without changing saved preferences."""
    st.session_state.settings_active_section = section


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
    saved_ai_preferences = settings.get("ai_preferences", {})
    if not isinstance(saved_ai_preferences, dict):
        saved_ai_preferences = {}
    for key, default in AI_PREFERENCE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = saved_ai_preferences.get(key, default)

    st.title("Settings")
    st.caption("Adjust the interface and learning support to suit your study preferences. Changes save automatically.")
    st.markdown(f"<div class='vc-muted'>{_current_summary(_current_widget_values(settings))}</div>", unsafe_allow_html=True)

    sections = [
        ("General", "Quick setups and guided tour"),
        ("Appearance", "Theme, typography and colours"),
        ("Learning", "Feedback and hint preferences"),
        ("Focus & sound", "Motion and answer sounds"),
        ("Reading comfort", "Text and spacing"),
        ("Notifications", "Notification preferences"),
        ("Account", "Account and sign-in options"),
        ("Privacy & safety", "Privacy notices and AI safety"),
        ("Socials", "Community links and social channels"),
        ("AI", "AI learning support and provider information"),
        ("Upgrade", "Plans and premium features"),
        ("Misc", "About Vocogni and other options"),
    ]
    active_section = st.session_state.get("settings_active_section", "General")
    if active_section not in {item[0] for item in sections}:
        active_section = "General"
        st.session_state.settings_active_section = active_section

    # Group the settings destinations by task so the page is scannable
    # without presenting twelve equally weighted buttons in one grid.
    st.markdown("### Settings categories")
    st.caption(f"Currently viewing **{active_section}**")
    category_groups = [
        ("Personalize", [("General", "Quick setups and guided tour"), ("Appearance", "Theme, typography and colours"), ("Focus & sound", "Motion and answer sounds"), ("Reading comfort", "Text and spacing")]),
        ("Learning", [("Learning", "Feedback and hint preferences"), ("AI", "AI learning support and provider preferences")]),
        ("Account & privacy", [("Account", "Account and sign-in options"), ("Privacy & safety", "Privacy notices and AI safety")]),
        ("More", [("Notifications", "Notification preferences"), ("Socials", "Community links and social channels"), ("Upgrade", "Plans and premium features"), ("Misc", "About Vocogni and other options")]),
    ]
    group_cols = st.columns(2, gap="medium")
    for group_index, (group_name, destinations) in enumerate(category_groups):
        with group_cols[group_index % 2]:
            with st.container(border=True):
                st.markdown(f"**{group_name}**")
                button_cols = st.columns(2, gap="small")
                for index, (name, description) in enumerate(destinations):
                    with button_cols[index % 2]:
                        st.button(
                            name,
                            key=f"settings_section_{name.lower().replace(' ', '_').replace('&', 'and')}",
                            type="primary" if active_section == name else "secondary",
                            use_container_width=True,
                            help=description,
                            on_click=_select_settings_section,
                            args=(name,),
                        )
    st.divider()

    if active_section == "General":
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

    if active_section == "Appearance":
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

    if active_section == "Learning":
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

    if active_section == "Focus & sound":
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


    if active_section == "Reading comfort":
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



    if active_section == "General":
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

    if active_section == "Notifications":
        with st.container(border=True):
            st.subheader("Notifications")
            st.caption("Notification controls will be added here in a future update.")
            st.info("No notification preferences are available yet.")

    if active_section == "Account":
        with st.container(border=True):
            st.subheader("Account")
            st.caption("Account and sign-in management will be added here in a future update.")
            st.info("No account-management controls are available here yet.")

    if active_section == "Socials":
        with st.container(border=True):
            st.subheader("Vocogni Socials")
            st.caption("Official community and social channels will appear here.")
            st.info("Social links are not configured yet. Only verified official links will be listed.")

    if active_section == "AI":
        st.subheader("AI preferences")
        st.caption(
            "Shape how a future Vocogni tutor should teach, explain, and adapt. "
            "The controls below are grouped by purpose so you can scan them quickly."
        )
        st.info(
            "These preferences are saved to your learner settings and shape the offline "
            "rule-based progress summary. No LLM or external AI provider is used here. "
            "Options requiring web access, image understanding, or a hosted model do not run in this prototype."
        )

        with st.expander("01 · Teaching approach", expanded=True):
            teaching_col, guidance_col = st.columns(2, gap="large")
            with teaching_col:
                st.selectbox(
                    "Teaching style",
                    ["Adaptive", "Socratic (ask me questions)", "Direct and concise", "Detailed instructor"],
                    key="ai_preview_teaching_style",
                    help="Choose how the future AI tutor should communicate and guide a lesson.",
                )
                st.select_slider(
                    "Explanation depth",
                    options=["Brief", "Balanced", "In-depth"],
                    key="ai_preview_explanation_depth",
                    help="Set the amount of reasoning and context in explanations.",
                )
            with guidance_col:
                st.selectbox(
                    "Hint strategy",
                    ["On request", "Progressive hints", "Guided questions", "Worked example first"],
                    key="ai_preview_hint_strategy",
                    help="Choose how support should be revealed when you are stuck.",
                )
                st.selectbox(
                    "Correction style",
                    ["Explain the misconception", "Show the corrected method", "Ask me to find the error"],
                    key="ai_preview_correction_style",
                    help="Choose how the future tutor should respond to an incorrect answer.",
                )

        with st.expander("02 · Adaptation & challenge", expanded=False):
            adaptation_col, challenge_col = st.columns(2, gap="large")
            with adaptation_col:
                st.toggle(
                    "Adapt to my demonstrated mastery",
                    key="ai_preview_adaptive_mastery",
                    help="Future AI could adjust support based on demonstrated understanding, not just speed.",
                )
                st.toggle(
                    "Remember learning preferences",
                    value=True,
                    key="ai_preview_remember_preferences",
                    help="Future AI could reuse your selected explanation and feedback preferences.",
                )
            with challenge_col:
                st.selectbox(
                    "Challenge level",
                    ["Adaptive", "Build confidence", "Standard", "Stretch me"],
                    key="ai_preview_challenge_level",
                    help="Set the intended level of challenge for future practice recommendations.",
                )
                st.toggle(
                    "Include transfer questions",
                    value=True,
                    key="ai_preview_transfer_questions",
                    help="Request questions that apply an idea in a new context.",
                )

        with st.expander("03 · Answer quality & sources", expanded=False):
            quality_col, source_col = st.columns(2, gap="large")
            with quality_col:
                st.toggle(
                    "Show reasoning steps",
                    value=True,
                    key="ai_preview_reasoning_steps",
                    help="Ask the future AI tutor to explain the main steps behind an answer.",
                )
                st.toggle(
                    "Double-check calculations",
                    value=True,
                    key="ai_preview_check_calculations",
                    help="Request an additional consistency check for mathematical results.",
                )
            with source_col:
                st.toggle(
                    "Show sources when available",
                    value=True,
                    key="ai_preview_show_sources",
                    help="Display references for claims that rely on external information.",
                )
                st.toggle(
                    "Flag uncertain answers",
                    value=True,
                    key="ai_preview_flag_uncertainty",
                    help="Make uncertainty explicit instead of presenting guesses as facts.",
                )

        with st.expander("04 · Interaction preferences", expanded=False):
            interaction_col, context_col = st.columns(2, gap="large")
            with interaction_col:
                st.toggle(
                    "Allow follow-up questions",
                    value=True,
                    key="ai_preview_follow_up_questions",
                    help="Let the future tutor ask short questions to check understanding.",
                )
                st.toggle(
                    "Use examples from everyday life",
                    value=True,
                    key="ai_preview_everyday_examples",
                    help="Prefer practical examples when they help explain a concept.",
                )
            with context_col:
                st.selectbox(
                    "Response language",
                    ["Match lesson language", "English", "Bahasa Indonesia", "Mandarin"],
                    key="ai_preview_response_language",
                    help="Choose the preferred language for future AI explanations.",
                )
                st.selectbox(
                    "Answer format",
                    ["Structured steps", "Short paragraphs", "Bullet points", "Exam-style response"],
                    key="ai_preview_answer_format",
                    help="Choose how future AI responses should be organized.",
                )

        with st.expander("05 · Model & capability preferences", expanded=False):
            model_col, capability_col = st.columns(2, gap="large")
            with model_col:
                st.selectbox(
                    "Model preference",
                    ["Automatic (recommended)", "Fast", "Balanced", "Advanced reasoning"],
                    key="ai_preview_model_preference",
                    help="A future provider integration could map this preference to available models.",
                )
                st.selectbox(
                    "Response speed",
                    ["Prioritize speed", "Balanced", "Prioritize depth"],
                    key="ai_preview_speed_preference",
                    help="Set the trade-off between response time and deeper analysis.",
                )
            with capability_col:
                st.toggle(
                    "Use web research when needed",
                    key="ai_preview_web_research",
                    help="Future AI could consult external sources for questions that need current information.",
                )
                st.toggle(
                    "Support image and worksheet input",
                    value=True,
                    key="ai_preview_image_input",
                    help="Prepare for future AI analysis of uploaded diagrams, images, and worksheets.",
                )

        with st.expander("06 · Boundaries & learner control", expanded=False):
            safety_col, privacy_col = st.columns(2, gap="large")
            with safety_col:
                st.toggle(
                    "Keep explanations age-appropriate",
                    value=True,
                    key="ai_preview_age_appropriate",
                    help="A future AI integration should keep explanations suitable for the learner's age.",
                )
                st.toggle(
                    "Stay within the lesson topic",
                    value=False,
                    key="ai_preview_lesson_scope",
                    help="Prefer answers focused on the current course unless broader context is requested.",
                )
            with privacy_col:
                st.toggle(
                    "Ask before using personal learning context",
                    value=True,
                    key="ai_preview_context_permission",
                    help="Future AI should request permission before using optional personal context.",
                )
                st.toggle(
                    "Let me review AI memory",
                    value=True,
                    key="ai_preview_memory_review",
                    help="A future memory feature should provide learner visibility and control.",
                )

        st.caption(
            "The local summary uses your saved practice statistics only. It cannot browse the web, "
            "interpret images, or provide a general-purpose tutoring conversation. Preferences for "
            "hosted-model capabilities are stored for future use but have no effect on this offline summary."
        )

    if active_section == "Upgrade":
        with st.container(border=True):
            st.subheader("Upgrade Vocogni")
            st.caption("Plan information and premium feature comparisons will be shown here.")
            st.info("No paid plans or upgrade actions are currently available.")

    if active_section == "Misc":
        with st.container(border=True):
            st.subheader("More")
            st.caption("Additional product information and small utilities.")
            st.markdown(f"**Vocogni version:** {APP_VERSION}")
            st.caption("Thanks for learning with Vocogni.")

    ai_preferences = {
        key: st.session_state.get(key, default)
        for key, default in AI_PREFERENCE_DEFAULTS.items()
    }
    if settings.get("ai_preferences") != ai_preferences:
        settings["ai_preferences"] = ai_preferences
        state.mark_persistent_dirty()

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

    if active_section == "Privacy & safety":
        st.divider()
        st.caption(f"Vocogni v{APP_VERSION}")

        st.divider()
        st.header("Terms, privacy & AI safety")
        st.caption("Read what the current prototype does, what learner data it uses, and the limits of its learning support.")
        render_legal_notices(st)
