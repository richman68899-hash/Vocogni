"""Vocogni's learner-data assistant.

The first version is intentionally grounded and private-by-default: it answers a
curated set of learning-support requests from the learner's current saved state.
It does not call an external model or transmit profile/progress data off-platform.
The pure request handler can be unit-tested without starting Streamlit.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import data
import logic


NAVIGATION_TARGETS = {
    "profile": "Profile",
    "progress": "Progress",
    "learn": "Browse",
    "browse": "Browse",
    "courses": "Browse",
    "course library": "Browse",
    "notes": "Notes",
    "settings": "Settings",
    "terms": "Settings",
    "terms of use": "Settings",
    "terms of service": "Settings",
    "privacy": "Settings",
    "privacy notice": "Settings",
    "privacy policy": "Settings",
    "ai safety": "Settings",
    "ai use and safety": "Settings",
    "ai use safety": "Settings",
    "safety notes": "Settings",
    "legal notices": "Settings",
}


def _normalise_query(query: str) -> str:
    """Lowercase and collapse punctuation/whitespace for predictable matching."""
    return " ".join(re.sub(r"[^a-z0-9\s'-]", " ", str(query).casefold()).split())


def _has_any(query: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in query for phrase in phrases)


def _profile_summary(profile: dict[str, Any] | None) -> str:
    profile = profile if isinstance(profile, dict) else {}
    lines = []
    name = str(profile.get("name") or "").strip()
    lines.append(f"**Learning profile{' — ' + name if name else ''}**")

    fields = (
        ("Grade", "grade"),
        ("Age", "age"),
        ("Country", "country"),
        ("Learning goals", "learning_goals"),
        ("Favourite subjects", "favorite_subjects"),
        ("Subjects you feel strongest in", "strong_subjects"),
        ("Subjects you want to improve", "weak_subjects"),
        ("Interests", "interests"),
        ("Career interests", "career_interests"),
        ("Learning style", "learning_style"),
        ("Preferred difficulty", "preferred_difficulty"),
        ("Preferred session length", "preferred_session_length"),
        ("Feedback preference", "preferred_feedback_style"),
        ("Preferred language", "preferred_language"),
    )
    included = 0
    for label, key in fields:
        value = profile.get(key)
        if isinstance(value, (list, tuple)):
            value = ", ".join(str(item).strip() for item in value if str(item).strip())
        value = str(value or "").strip()
        if not value or value.casefold() in {"prefer not to say", "not set", "none"}:
            continue
        lines.append(f"- **{label}:** {value}")
        included += 1

    if not name and included == 0:
        return (
            "**Your learning profile is mostly blank.** You can add optional "
            "details on the Profile page so Vocogni can give more relevant "
            "learning support. No profile information is required to use courses."
        )
    if included == 0:
        lines.append("There are no other profile preferences recorded yet.")
    lines.append("\nThis is a summary of fields in your Vocogni profile, not an inferred assessment.")
    return "\n".join(lines)


def _timestamp_key(value: Any) -> float:
    """Convert an ISO timestamp to a sortable UTC timestamp; unknown dates sort first."""
    if not value:
        return 0.0
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.timestamp()
    except (TypeError, ValueError, OverflowError):
        return 0.0


def _format_timestamp(value: Any) -> str:
    if not value:
        return "date not recorded"
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OverflowError):
        return "date not recorded"


def _recent_mistakes(progress: dict[str, Any] | None, limit: int = 5) -> list[dict[str, Any]]:
    """Collect incorrect answers from saved practice attempts, newest first."""
    progress = progress if isinstance(progress, dict) else {}
    mistakes: list[dict[str, Any]] = []

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        if not course:
            continue
        course_progress = progress.get(course_id, {})
        if not isinstance(course_progress, dict):
            continue
        attempt_map = course_progress.get("practice_attempts", {})
        if not isinstance(attempt_map, dict):
            continue

        for lesson_id, attempts in attempt_map.items():
            if not isinstance(attempts, list):
                continue
            lesson, _ = data.get_lesson(course_id, str(lesson_id))
            lesson_title = (
                str(lesson.get("title") or lesson_id)
                if isinstance(lesson, dict)
                else str(lesson_id)
            )
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    continue
                completed_at = attempt.get("completed_at")
                results = attempt.get("results", [])
                if not isinstance(results, list):
                    continue
                for result in results:
                    if not isinstance(result, dict) or result.get("correct") is not False:
                        continue
                    label = (
                        result.get("mistake_tag")
                        or result.get("skill_tag")
                        or result.get("skill_id")
                        or result.get("question_id")
                        or "Incorrect answer (no skill label saved)"
                    )
                    mistakes.append({
                        "course_id": course_id,
                        "course_title": str(course.get("title") or course.get("topic_label") or course_id),
                        "lesson_title": lesson_title,
                        "label": str(label),
                        "completed_at": completed_at,
                        "timestamp_key": _timestamp_key(completed_at),
                    })

    mistakes.sort(key=lambda item: item["timestamp_key"], reverse=True)
    return mistakes[:max(1, limit)]


def _mistakes_summary(progress: dict[str, Any] | None) -> str:
    recent = _recent_mistakes(progress)
    if recent:
        lines = ["**Your latest recorded mistakes**", ""]
        for index, item in enumerate(recent, start=1):
            lines.append(
                f"{index}. **{item['label']}** — {item['course_title']} · "
                f"{item['lesson_title']} · {_format_timestamp(item['completed_at'])}"
            )
        lines.extend([
            "",
            "These are incorrect responses in saved practice-attempt records. "
            "They show where to review, not proof of a fixed misconception.",
        ])
        return "\n".join(lines)

    progress = progress if isinstance(progress, dict) else {}
    aggregate = []
    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        course_progress = progress.get(course_id, {})
        if not course or not isinstance(course_progress, dict):
            continue
        tags = course_progress.get("mistakes", {})
        if not isinstance(tags, dict):
            continue
        for tag, raw_count in tags.items():
            try:
                count = int(raw_count)
            except (TypeError, ValueError, OverflowError):
                continue
            if count > 0:
                aggregate.append((count, str(course.get("title") or course_id), str(tag)))
    aggregate.sort(key=lambda item: (-item[0], item[1].casefold(), item[2].casefold()))
    if not aggregate:
        return (
            "I couldn't find any recorded incorrect practice answers yet. "
            "Once you complete lessons or practice, I can use the saved results to identify review topics."
        )

    lines = [
        "**Recorded mistake themes**",
        "",
        "The available history contains aggregate counters rather than item timestamps, "
        "so I can't reliably label these as the latest mistakes. These are the most frequent recorded themes:",
    ]
    for count, course_title, tag in aggregate[:5]:
        lines.append(f"- **{tag}** — {course_title} · {count} recorded error{'s' if count != 1 else ''}")
    return "\n".join(lines)


def _progress_summary(progress: dict[str, Any] | None) -> str:
    progress = progress if isinstance(progress, dict) else {}
    stats = logic.overall_stats(progress)
    questions = int(stats.get("questions_attempted", 0) or 0)
    correct = int(stats.get("correct_answers", 0) or 0)
    accuracy = (correct / questions * 100) if questions else None
    lines = [
        "**Your learning snapshot**",
        "",
        f"- Courses started: **{stats.get('courses_attempted', 0)}**",
        f"- Courses completed: **{stats.get('courses_completed', 0)}**",
        f"- Lessons completed: **{stats.get('lessons_completed', 0)}**",
        f"- Practice questions answered: **{questions}**",
        f"- Correct answers: **{correct}**",
        f"- Overall recorded accuracy: **{accuracy:.0f}%**" if accuracy is not None else "- Overall recorded accuracy: **not available yet**",
    ]
    if not questions:
        lines.extend(["", "Start a lesson or revision sprint to build a useful baseline."])
    else:
        attempted = [item for item in logic.per_course_stats(progress) if item.get("questions_attempted", 0)]
        attempted.sort(key=lambda item: (item.get("accuracy") if item.get("accuracy") is not None else -1, item.get("topic_label", "")))
        if attempted:
            weakest = attempted[0]
            strongest = attempted[-1]
            lines.extend([
                "",
                f"- Lowest recorded practice accuracy: **{weakest['topic_label']}** ({weakest['accuracy']:.0f}%)",
                f"- Highest recorded practice accuracy: **{strongest['topic_label']}** ({strongest['accuracy']:.0f}%)",
                "",
                "These are descriptive summaries of saved practice, not official grades or validated mastery scores.",
            ])
    return "\n".join(lines)


def _next_step_summary(progress: dict[str, Any] | None) -> str:
    progress = progress if isinstance(progress, dict) else {}
    coach = logic.get_mistake_coach(progress)
    if coach:
        lines = [
            "**Recommended next step**",
            "",
            f"**Focus:** {coach.get('skill', 'Review a recent error')}",
            f"**Evidence:** {coach.get('evidence_label', 'Saved practice history')}",
            f"**Why it matters:** {coach.get('why', 'Review the underlying method.')}",
            f"**Try this:** {coach.get('action', 'Revisit the related lesson and practise again.')}",
        ]
        destinations = coach.get("available_course_ids", [])
        if destinations:
            course = data.get_course(destinations[0])
            if course:
                lines.append(f"**Suggested course:** {course.get('title', destinations[0])}")
        lines.append("\nThis recommendation is rule-based and uses recorded mistake counts.")
        return "\n".join(lines)

    recommendations = logic.generate_recommendations(progress)
    if recommendations:
        return "**Useful next steps**\n\n" + "\n".join(f"- {item}" for item in recommendations)
    return (
        "I don't have enough saved practice history to personalise a next step yet. "
        "Start a course, complete its entry check, and answer a few practice questions first."
    )


def _courses_summary() -> str:
    lines = ["**Courses in your learning library**", ""]
    for course in data.all_courses_in_order():
        title = str(course.get("title") or course.get("topic_label") or course.get("id"))
        description = str(course.get("short_description") or "").strip()
        subject = str(course.get("subject_label") or "").strip()
        lesson_count = course.get("lesson_count", len(course.get("lessons", [])))
        details = " · ".join(value for value in (subject, f"{lesson_count} lessons") if value)
        lines.append(f"- **{title}**" + (f" — {description}" if description else "") + (f" ({details})" if details else ""))
    lines.extend(["", "Open Learn to search the library and filter by topic, difficulty, category, or subject."])
    return "\n".join(lines)


def _notes_summary(notes: Any, milestones: Any) -> str:
    notes = notes if isinstance(notes, list) else []
    milestones = milestones if isinstance(milestones, list) else []
    lines = [
        "**Your saved workspace**",
        "",
        f"- Notes: **{len([item for item in notes if isinstance(item, dict)])}**",
        f"- Learning milestones: **{len([item for item in milestones if isinstance(item, dict)])}**",
    ]
    note_titles = [
        str(item.get("title") or "Untitled note").strip()
        for item in notes if isinstance(item, dict)
    ]
    if note_titles:
        lines.extend(["", "**Recent note titles**"])
        lines.extend(f"- {title}" for title in note_titles[:5])
    if not note_titles and not milestones:
        lines.extend(["", "Your workspace is empty for now. Create a note or milestone to keep track of ideas and goals."])
    return "\n".join(lines)


def _settings_summary(settings: dict[str, Any] | None) -> str:
    settings = settings if isinstance(settings, dict) else {}
    labels = (
        ("Appearance", "appearance"),
        ("Text size", "text_size"),
        ("Feedback timing", "feedback_timing"),
        ("Hint assistance", "difficulty"),
        ("Motion", "animations"),
        ("Larger text", "larger_text"),
        ("High-readability spacing", "high_readability"),
    )
    lines = ["**Your learning settings**", ""]
    for label, key in labels:
        value = settings.get(key)
        if value is None:
            continue
        if isinstance(value, bool):
            value = "On" if value else "Off"
        lines.append(f"- **{label}:** {value}")
    if len(lines) == 2:
        lines.append("No display preferences are available in the current session.")
    lines.extend(["", "To change these preferences, open Settings from the sidebar."])
    return "\n".join(lines)


def _navigation_target(query: str) -> str | None:
    navigation_verbs = ("open ", "go to ", "take me to ", "navigate to ", "switch to ", "show me the page ")
    if not query.startswith(navigation_verbs):
        return None
    trimmed = query
    for prefix in navigation_verbs:
        if trimmed.startswith(prefix):
            trimmed = trimmed[len(prefix):]
            break
    trimmed = re.sub(r"\b(page|section|screen)\b", "", trimmed).strip()
    for alias, route in NAVIGATION_TARGETS.items():
        if trimmed == alias or trimmed.startswith(alias + " "):
            return route
    return None


def answer_request(
    query: str,
    profile: dict[str, Any] | None,
    progress: dict[str, Any] | None,
    settings: dict[str, Any] | None = None,
    notes: Any = None,
    milestones: Any = None,
) -> tuple[str, str | None]:
    """Return (grounded reply, optional navigation route) for supported requests."""
    normalized = _normalise_query(query)
    if not normalized:
        return "Type a request or choose one of the quick actions.", None

    route = _navigation_target(normalized)
    if route:
        labels = {"Profile": "profile", "Progress": "progress", "Browse": "Learn / course library", "Notes": "Notes", "Settings": "Settings"}
        return f"Opening **{labels.get(route, route)}**.", route

    if _has_any(normalized, ("terms of service", "terms of use", "privacy notice", "privacy policy", "ai safety", "ai use and safety", "ai use safety", "safety notes", "legal notices")):
        return (
            "Vocogni's draft Terms of Use, Privacy Notice, and AI Use & Safety Notes are available in **Settings**, near the bottom of the page. They are working drafts, not final legal terms or proof of compliance. The Study Guide is rule-based and does not call a generative AI model in this build.",
            "Settings",
        )

    if _has_any(normalized, ("help", "what can you do", "commands", "supported requests", "how can you help")):
        return (
            "**What I can help with**\n\n"
            "- Summarise your learning profile.\n"
            "- Show recent recorded mistakes (or aggregate mistake themes when timestamps aren't available).\n"
            "- Summarise your progress and practice accuracy.\n"
            "- Recommend a next learning step from recorded activity.\n"
            "- List courses in your library.\n"
            "- Summarise your notes and learning milestones.\n"
            "- Show your learning settings.\n"
            "- Open Profile, Progress, Learn, Notes, or Settings.\n"
            "- Open Settings to read the Terms, Privacy Notice, and AI Use & Safety Notes.\n\n"
            "The Study Guide uses data already in Vocogni. It does not infer missing results or invent a learning history."
        ), None

    if _has_any(normalized, ("profile", "about me", "learning goals", "my interests")):
        return _profile_summary(profile), None
    if _has_any(normalized, ("mistake", "mistakes", "wrong answer", "wrong answers", "errors", "incorrect answer")):
        return _mistakes_summary(progress), None
    if _has_any(normalized, ("progress", "how am i doing", "my stats", "statistics", "performance", "learning snapshot")):
        return _progress_summary(progress), None
    if _has_any(normalized, ("next step", "what should i study", "what to study", "recommend", "recommendation", "what next", "practise next", "practice next")):
        return _next_step_summary(progress), None
    if _has_any(normalized, ("available courses", "list courses", "show courses", "course library", "what courses")):
        return _courses_summary(), None
    if _has_any(normalized, ("my notes", "summarise notes", "summarize notes", "workspace", "milestone", "milestones")):
        return _notes_summary(notes, milestones), None
    if _has_any(normalized, ("setting", "settings", "preferences", "text size", "dark mode", "appearance")):
        return _settings_summary(settings), None

    return (
        "The Study Guide does not support that request yet. Try **Help** or one of these requests: "
        "**summarise my profile**, **show my latest mistakes**, **summarise my progress**, "
        "**recommend my next step**, or **list courses**.\n\n"
        "For explanations of a subject, open the related lesson and use its worked examples and practice feedback.",
        None,
    )


_ASSISTANT_CSS = """
<style>
.st-key-vocogni_assistant_launcher {
    position: fixed !important;
    right: 1.25rem !important;
    bottom: 1.15rem !important;
    width: auto !important;
    max-width: calc(100vw - 2rem) !important;
    z-index: 10000 !important;
}
.st-key-vocogni_assistant_launcher button {
    border-radius: 999px !important;
    min-height: 3.05rem !important;
    padding: 0.7rem 1.15rem !important;
    box-shadow: 0 8px 26px rgba(0, 0, 0, 0.18) !important;
    font-weight: 650 !important;
}
.st-key-vocogni_assistant_panel {
    position: fixed !important;
    right: 1.25rem !important;
    bottom: 5.25rem !important;
    width: min(410px, calc(100vw - 2rem)) !important;
    max-height: min(72vh, 650px) !important;
    overflow-y: auto !important;
    padding: 1rem !important;
    background: var(--vc-surface, #fff) !important;
    color: var(--vc-text, #182831) !important;
    border: 1px solid var(--vc-border, #d8e1dc) !important;
    border-radius: 16px !important;
    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.24) !important;
    z-index: 9999 !important;
}
.st-key-vocogni_assistant_panel [data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}
.st-key-vocogni_assistant_panel [data-testid="stChatMessage"] {
    padding: 0.65rem 0.75rem;
    border-radius: 10px;
}
.st-key-vocogni_assistant_panel [data-testid="stChatMessage"] p {
    font-size: 0.9rem;
}
.st-key-vocogni_assistant_panel [data-testid="stTextInput"] input {
    min-height: 2.8rem !important;
}
@media (max-width: 640px) {
    .st-key-vocogni_assistant_launcher {
        right: 0.75rem !important;
        bottom: 0.75rem !important;
    }
    .st-key-vocogni_assistant_launcher button {
        min-height: 2.8rem !important;
        padding: 0.6rem 0.9rem !important;
    }
    .st-key-vocogni_assistant_panel {
        left: 0.5rem !important;
        right: 0.5rem !important;
        bottom: 4.5rem !important;
        width: auto !important;
        max-height: 72vh !important;
    }
}
</style>
"""


def render_assistant(
    st: Any,
    profile: dict[str, Any] | None,
    progress: dict[str, Any] | None,
    settings: dict[str, Any] | None = None,
    notes: Any = None,
    milestones: Any = None,
) -> None:
    """Render the floating assistant only when the caller is on Learn/Browse."""
    st.session_state.setdefault("vocogni_assistant_open", False)
    st.session_state.setdefault("vocogni_assistant_messages", [])
    st.markdown(_ASSISTANT_CSS, unsafe_allow_html=True)

    with st.container(key="vocogni_assistant_launcher"):
        button_label = "Close Study Guide" if st.session_state.vocogni_assistant_open else "Study Guide"
        if st.button(button_label, key="vocogni_assistant_toggle", type="primary"):
            st.session_state.vocogni_assistant_open = not st.session_state.vocogni_assistant_open
            st.rerun()

    if not st.session_state.vocogni_assistant_open:
        return

    with st.container(key="vocogni_assistant_panel"):
        title_col, close_col = st.columns([5, 1], vertical_alignment="center")
        with title_col:
            st.markdown("### Vocogni Study Guide")
            st.caption("A rule-based guide to your profile, progress, mistakes, and next steps")
            st.caption(
                "Prototype disclosure: replies are rule-based and use data already in Vocogni; "
                "this build does not call a generative AI model. Avoid passwords and sensitive "
                "personal information. The full draft notices are available in Settings."
            )
            if st.button(
                "Read Terms, Privacy & AI Safety",
                key="vocogni_assistant_policy_button",
                use_container_width=True,
            ):
                st.session_state.nav = "Settings"
                st.session_state.vocogni_assistant_open = False
                st.rerun()
        with close_col:
            if st.button("✕", key="vocogni_assistant_close", help="Close Study Guide"):
                st.session_state.vocogni_assistant_open = False
                st.rerun()

        messages = st.session_state.vocogni_assistant_messages

        # Keep the prompt shortcuts visible throughout the conversation.
        # Learners can start with a suggestion or use one again after seeing
        # a reply; the shortcuts do not clear or replace the conversation.
        st.markdown("**Quick requests**")
        st.caption("Choose a prompt at any time, or write your own message below.")
        quick_col1, quick_col2 = st.columns(2, gap="small")
        quick_request = None
        with quick_col1:
            if st.button("Summarise profile", key="vocogni_assistant_quick_profile", use_container_width=True):
                quick_request = "summarise my profile"
            if st.button("Latest mistakes", key="vocogni_assistant_quick_mistakes", use_container_width=True):
                quick_request = "show my latest mistakes"
        with quick_col2:
            if st.button("My progress", key="vocogni_assistant_quick_progress", use_container_width=True):
                quick_request = "summarise my progress"
            if st.button("Next step", key="vocogni_assistant_quick_next", use_container_width=True):
                quick_request = "recommend my next step"

        # Show a bounded conversation window to keep the floating panel usable.
        for message in messages[-8:]:
            with st.chat_message(message.get("role", "assistant")):
                st.markdown(str(message.get("content", "")))

        with st.form("vocogni_assistant_form", clear_on_submit=True):
            query = st.text_input(
                "Message",
                placeholder="e.g. Show my latest mistakes",
                label_visibility="collapsed",
                max_chars=240,
                key="vocogni_assistant_query",
            )
            submitted = st.form_submit_button("Send", type="primary", use_container_width=True)

        if submitted or quick_request:
            chosen_query = str(query if submitted else quick_request).strip()
            if chosen_query:
                messages.append({"role": "user", "content": chosen_query})
                reply, route = answer_request(
                    chosen_query,
                    profile,
                    progress,
                    settings=settings,
                    notes=notes,
                    milestones=milestones,
                )
                messages.append({"role": "assistant", "content": reply})
                st.session_state.vocogni_assistant_messages = messages[-20:]
                if route:
                    st.session_state.nav = route
                    st.session_state.vocogni_assistant_open = False
                st.rerun()
