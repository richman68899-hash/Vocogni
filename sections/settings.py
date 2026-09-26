"""sections/settings.py — Settings (spec section 15).

Every control here writes straight back into st.session_state.settings, so
changes apply immediately (no separate Save step) and are picked up by
styles.build_css() and by the lesson flow in sections/course.py.
"""

import streamlit as st


def render():
    st.markdown("<h2>Settings</h2>", unsafe_allow_html=True)
    settings = st.session_state.settings

    st.markdown("<h3>Appearance</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        appearance = st.radio(
            "Theme", ["Light", "Dark"],
            index=["Light", "Dark"].index(settings["appearance"]),
            horizontal=True,
        )
    with c2:
        text_size = st.radio(
            "Text size", ["Small", "Medium", "Large"],
            index=["Small", "Medium", "Large"].index(settings["text_size"]),
            horizontal=True,
        )

    st.markdown("<h3 style='margin-top:1.2rem;'>Learning experience</h3>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        feedback_timing = st.radio(
            "Feedback", ["Immediate", "After submission"],
            index=["Immediate", "After submission"].index(settings["feedback_timing"]),
            horizontal=True,
            help="Immediate shows correctness right after each question. "
                 "After submission shows a combined summary at the end of the lesson.",
        )
    with c4:
        difficulty = st.radio(
            "Difficulty", ["Adaptive", "Easy", "Medium", "Hard"],
            index=["Adaptive", "Easy", "Medium", "Hard"].index(settings["difficulty"]),
            horizontal=True,
            help="Prototype preference. Easy also shows a hint on numeric questions.",
        )

    st.markdown("<h3 style='margin-top:1.2rem;'>Interaction</h3>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        animations = st.toggle("Animations", value=settings["animations"])
    with c6:
        sound = st.toggle("Sound", value=settings["sound"], help="Plays a short tone on a correct answer.")

    st.markdown("<h3 style='margin-top:1.2rem;'>Accessibility</h3>", unsafe_allow_html=True)
    reduced_motion = st.checkbox(
        "Reduced motion", value=settings["reduced_motion"],
        help="Turns off transitions and animated effects throughout the app.",
    )
    larger_text = st.checkbox(
        "Larger text", value=settings["larger_text"],
        help="Increases the base text size beyond the Text size option above.",
    )
    high_readability = st.checkbox(
        "High readability mode", value=settings["high_readability"],
        help="Increases line spacing to make longer text easier to read.",
    )
    st.markdown(
        "<p class='vc-muted' style='margin-top:0.6rem;'>These accessibility options "
        "only adjust spacing, motion, and text size. VOCogni does not make medical "
        "claims about ADHD or neurodivergence.</p>",
        unsafe_allow_html=True,
    )

    settings.update({
        "appearance": appearance,
        "text_size": text_size,
        "feedback_timing": feedback_timing,
        "difficulty": difficulty,
        "animations": animations,
        "sound": sound,
        "reduced_motion": reduced_motion,
        "larger_text": larger_text,
        "high_readability": high_readability,
    })