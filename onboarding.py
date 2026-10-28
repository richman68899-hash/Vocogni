"""First-run guided tour for Vocogni.

The tour uses the existing Streamlit session and durable settings bundle. It
adds no database columns and deliberately does not modify course progress.
"""
from __future__ import annotations

import html
from typing import Any


TUTORIAL_STEPS: tuple[dict[str, str], ...] = (
    {
        "eyebrow": "WELCOME",
        "short_title": "Welcome",
        "title": "Learn with a clearer next step.",
        "body": (
            "Vocogni brings lessons, deliberate practice, and progress evidence "
            "into one learning workspace."
        ),
        "detail": (
            "This quick tour shows you where things live. It will not create "
            "practice attempts or change your results."
        ),
        "route": "Browse",
    },
    {
        "eyebrow": "01 · LEARN",
        "short_title": "Learn",
        "title": "Start with a course, not a blank page.",
        "body": (
            "Use Learn to browse subjects and open a course. Lessons guide you "
            "from a concept explanation into questions you can work through."
        ),
        "detail": (
            "Some courses include an entry diagnostic to help choose a starting "
            "route. You can browse first; this tour will not enrol you or start a lesson."
        ),
        "route": "Browse",
    },
    {
        "eyebrow": "02 · PRACTISE",
        "short_title": "Practice",
        "title": "Turn practice into a useful next action.",
        "body": (
            "Use lesson questions to check your understanding. The Personalized "
            "Revision Sprint can assemble supported questions around your saved "
            "activity and priority skills."
        ),
        "detail": (
            "Practice scores are learning evidence, not official exam marks or "
            "predicted school grades. The available question set depends on the course."
        ),
        "route": "Browse",
    },
    {
        "eyebrow": "03 · PROGRESS",
        "short_title": "Progress",
        "title": "Look for patterns, not just a score.",
        "body": (
            "Progress brings together completed lessons, recorded practice, "
            "recurring mistakes, skill evidence, and suggested next actions."
        ),
        "detail": (
            "Some tracking is still a prototype. Use the evidence to decide what "
            "to review, rather than treating it as a validated mastery assessment."
        ),
        "route": "Progress",
    },
    {
        "eyebrow": "04 · NOTES",
        "short_title": "Notes",
        "title": "Keep the ideas worth revisiting.",
        "body": (
            "Create notes, organise them into folders, and use milestones with "
            "checklists to keep a learning goal manageable."
        ),
        "detail": (
            "Notes and milestones are saved with your learner data. You can return "
            "to them as you study."
        ),
        "route": "Notes",
    },
    {
        "eyebrow": "05 · PROFILE",
        "short_title": "Profile",
        "title": "Give your learning workspace context.",
        "body": (
            "Use your profile to record relevant learning goals, subjects, "
            "interests, and preferences."
        ),
        "detail": (
            "Only enter details you are comfortable saving. Vocogni should use "
            "recorded information as context, not guess at details you have not provided."
        ),
        "route": "Profile",
    },
    {
        "eyebrow": "06 · ASSISTANT",
        "short_title": "Assistant",
        "title": "Ask for help from the Learn area.",
        "body": (
            "The Vocogni Assistant can help you navigate supported features and "
            "summarise information already recorded in your learning data."
        ),
        "detail": (
            "Try requests such as “show my progress”, “list courses”, or “show my "
            "recent mistakes”. It should not invent results when evidence is missing."
        ),
        "route": "Browse",
    },
    {
        "eyebrow": "07 · SETTINGS",
        "short_title": "Settings",
        "title": "Make the workspace work for you.",
        "body": (
            "Settings lets you adjust appearance, text size, interface font, "
            "colour, feedback timing, hint assistance, and motion preferences."
        ),
        "detail": (
            "You can replay this guided tour from Settings at any time, including "
            "after you finish it."
        ),
        "route": "Settings",
    },
)


def is_tutorial_complete(settings: Any) -> bool:
    """Treat only the explicit boolean True as completed; old records default to false."""
    return isinstance(settings, dict) and settings.get("tutorial_completed") is True


def normalize_step_index(value: Any) -> int:
    """Clamp persisted/session input to a valid tutorial step index."""
    if isinstance(value, bool):
        return 0
    try:
        index = int(value)
    except (TypeError, ValueError, OverflowError):
        return 0
    return max(0, min(index, len(TUTORIAL_STEPS) - 1))


def get_tutorial_step(value: Any) -> dict[str, str]:
    """Return a safe step record for the supplied index."""
    return TUTORIAL_STEPS[normalize_step_index(value)]


def _set_tutorial_step(value: int) -> None:
    """Streamlit callback: move the guide and the underlying page together."""
    import streamlit as st

    index = normalize_step_index(value)
    st.session_state["tutorial_step"] = index
    st.session_state["nav"] = TUTORIAL_STEPS[index]["route"]


def start_tutorial() -> None:
    """Streamlit callback: restart the guide without touching learning progress."""
    import streamlit as st
    import state

    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}
        st.session_state["settings"] = settings

    settings["tutorial_completed"] = False
    st.session_state["tutorial_step"] = 0
    st.session_state["nav"] = "Browse"
    state.mark_persistent_dirty()


def _complete_tutorial() -> None:
    """Streamlit callback: save completion through the existing autosave flow."""
    import streamlit as st
    import state

    settings = st.session_state.get("settings")
    if not isinstance(settings, dict):
        settings = {}
        st.session_state["settings"] = settings

    settings["tutorial_completed"] = True
    st.session_state.pop("tutorial_step", None)
    st.session_state["nav"] = "Browse"
    state.mark_persistent_dirty()


def render_tutorial(st: Any) -> None:
    """Render a compact, accessible guide card above the current page."""
    settings = st.session_state.get("settings", {})
    if is_tutorial_complete(settings):
        return

    index = normalize_step_index(st.session_state.get("tutorial_step", 0))
    st.session_state["tutorial_step"] = index
    step = TUTORIAL_STEPS[index]
    is_last = index == len(TUTORIAL_STEPS) - 1
    percent = int(((index + 1) / len(TUTORIAL_STEPS)) * 100)

    eyebrow = html.escape(step["eyebrow"])
    title = html.escape(step["title"])
    body = html.escape(step["body"])
    detail = html.escape(step["detail"])
    step_label = f"Step {index + 1} of {len(TUTORIAL_STEPS)}"
    st.markdown(
        f"""
        <section role="region" aria-label="Vocogni guided tour"
          style="margin:0 0 1.25rem 0;padding:1.15rem 1.2rem 1.1rem;
          border:1px solid var(--vc-border);border-radius:12px;
          background:var(--vc-surface);">
          <div style="display:flex;gap:.75rem;align-items:center;margin-bottom:.85rem;">
            <div aria-hidden="true" style="display:flex;align-items:center;justify-content:center;
              width:42px;height:42px;flex:0 0 42px;border-radius:10px;
              background:var(--vc-accent);color:var(--vc-on-accent);
              font-size:1.2rem;font-weight:750;letter-spacing:-.05em;">V</div>
            <div>
              <div style="font-weight:700;letter-spacing:-.02em;color:var(--vc-text);">Vocogni guide</div>
              <div style="font-size:.82rem;color:var(--vc-subtext);">{html.escape(step_label)}</div>
            </div>
            <div style="margin-left:auto;font-size:.76rem;font-weight:650;
              color:var(--vc-subtext);white-space:nowrap;">{percent}%</div>
          </div>
          <div style="height:4px;background:var(--vc-surface-alt);border-radius:999px;overflow:hidden;margin:0 0 1rem;">
            <div style="height:100%;width:{percent}%;background:var(--vc-accent);border-radius:999px;"></div>
          </div>
          <div style="font-size:.7rem;font-weight:750;letter-spacing:.09em;
            color:var(--vc-accent);margin-bottom:.35rem;">{eyebrow}</div>
          <h2 style="font-size:1.28rem;line-height:1.25;letter-spacing:-.035em;
            color:var(--vc-text);margin:0 0 .5rem 0;">{title}</h2>
          <p style="font-size:.94rem;line-height:1.62;color:var(--vc-text);margin:0 0 .6rem 0;">{body}</p>
          <p style="font-size:.84rem;line-height:1.55;color:var(--vc-subtext);
            margin:0;padding-left:.75rem;border-left:2px solid var(--vc-border);">{detail}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    skip_col, back_col, next_col = st.columns([1.05, 0.85, 1.4], gap="small")
    with skip_col:
        st.button(
            "Skip tour",
            key="tutorial_skip",
            on_click=_complete_tutorial,
            use_container_width=True,
        )
    with back_col:
        st.button(
            "Back",
            key="tutorial_back",
            disabled=index == 0,
            on_click=_set_tutorial_step,
            args=(index - 1,),
            use_container_width=True,
        )
    with next_col:
        if is_last:
            st.button(
                "Finish tutorial",
                key="tutorial_finish",
                type="primary",
                on_click=_complete_tutorial,
                use_container_width=True,
            )
        else:
            destination = TUTORIAL_STEPS[index + 1]["short_title"]
            label = "Start tour" if index == 0 else f"Next: {destination}"
            st.button(
                label,
                key="tutorial_next",
                type="primary",
                on_click=_set_tutorial_step,
                args=(index + 1,),
                use_container_width=True,
            )
