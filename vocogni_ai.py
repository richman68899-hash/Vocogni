"""Integrated Vocogni Study Guide with opt-in external LLM tutoring.

Deterministic account commands remain local. Open-ended tutoring uses the optional
OpenAI-compatible provider only after an explicit, session-only learner opt-in.
"""
from __future__ import annotations

import os
from typing import Any

import logic
from ai_prototype.engine import answer as generate_ai_answer
from ai_prototype.llm import is_configured
from vocogni_assistant import answer_request, _recent_mistakes


_UNHANDLED_PREFIX = "The Study Guide does not support that request yet."


def _provider_config(st: Any) -> dict[str, str]:
    """Read provider settings from Streamlit secrets or environment variables."""
    config = {
        "base_url": os.getenv("VOCogni_LLM_BASE_URL", "").strip(),
        "model": os.getenv("VOCogni_LLM_MODEL", "").strip(),
        "api_key": os.getenv("VOCogni_LLM_API_KEY", "").strip(),
    }
    try:
        section = st.secrets.get("llm", {})
        if section:
            for key in ("base_url", "model", "api_key"):
                value = section.get(key)
                if value:
                    config[key] = str(value).strip()
    except Exception:
        pass
    return config


def _learner_context(
    profile: dict[str, Any] | None,
    progress: dict[str, Any] | None,
) -> str:
    """Build a small teaching context; exclude identity and private workspace data."""
    profile = profile if isinstance(profile, dict) else {}
    progress = progress if isinstance(progress, dict) else {}
    lines: list[str] = []

    # Only grade level and learning preferences are included from the profile.
    for label, key in (
        ("Grade level", "grade"),
        ("Preferred language", "preferred_language"),
        ("Preferred difficulty", "preferred_difficulty"),
        ("Feedback preference", "preferred_feedback_style"),
    ):
        value = profile.get(key)
        if isinstance(value, (list, tuple)):
            value = ", ".join(str(item).strip() for item in value if str(item).strip())
        value = str(value or "").strip()
        if value and value.casefold() not in {"not set", "none", "prefer not to say"}:
            lines.append(f"{label}: {value[:120]}")

    stats = logic.overall_stats(progress)
    attempted = int(stats.get("questions_attempted", 0) or 0)
    correct = int(stats.get("correct_answers", 0) or 0)
    if attempted:
        lines.append(
            f"Recorded practice: {correct}/{attempted} correct "
            f"({correct / attempted * 100:.0f}% overall accuracy)."
        )

    course_rows = [
        row for row in logic.per_course_stats(progress)
        if int(row.get("questions_attempted", 0) or 0) > 0
    ]
    if course_rows:
        course_rows.sort(key=lambda row: str(row.get("topic_label", "")))
        summaries = []
        for row in course_rows[:6]:
            accuracy = row.get("accuracy")
            if accuracy is not None:
                summaries.append(f"{row.get('topic_label', 'Course')}: {accuracy:.0f}%")
        if summaries:
            lines.append("Recorded course accuracy: " + "; ".join(summaries) + ".")

    recent = _recent_mistakes(progress, limit=5)
    if recent:
        tags = []
        for item in recent:
            label = str(item.get("label", "")).strip()
            course = str(item.get("course_title", "")).strip()
            if label:
                tags.append(f"{label} ({course})" if course else label)
        if tags:
            lines.append(
                "Recent recorded mistake tags (not learner working and not confirmed misconceptions): "
                + "; ".join(tags)
                + "."
            )

    return "\n".join(lines) if lines else "No learner learning-context data is available yet."


def _recent_ai_history(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Include only user/assistant pairs from earlier external-AI tutoring turns.

    Local profile, notes, and progress summaries are intentionally excluded.
    """
    result: list[dict[str, str]] = []
    for index, item in enumerate(messages):
        if not isinstance(item, dict):
            continue
        if item.get("role") == "assistant" and item.get("mode") == "llm":
            result.append({"role": "assistant", "content": str(item.get("content", ""))[:2500]})
            previous = messages[index - 1] if index > 0 else None
            if isinstance(previous, dict) and previous.get("role") == "user":
                result.insert(
                    max(0, len(result) - 1),
                    {"role": "user", "content": str(previous.get("content", ""))[:2500]},
                )
    return result[-8:]


def _is_unhandled(reply: str, route: str | None) -> bool:
    return route is None and str(reply).startswith(_UNHANDLED_PREFIX)


def render_assistant(
    st: Any,
    profile: dict[str, Any] | None,
    progress: dict[str, Any] | None,
    settings: dict[str, Any] | None = None,
    notes: Any = None,
    milestones: Any = None,
) -> None:
    """Render the learner assistant with local commands and opt-in LLM tutoring."""
    st.session_state.setdefault("vocogni_assistant_open", False)
    st.session_state.setdefault("vocogni_assistant_messages", [])
    st.session_state.setdefault("vocogni_ai_opt_in", False)

    provider_config = _provider_config(st)
    provider_ready = is_configured(provider_config)

    with st.sidebar.container(key="vocogni_assistant_launcher"):
        button_label = "Close Study Guide" if st.session_state.vocogni_assistant_open else "Study Guide"
        if st.button(button_label, key="vocogni_assistant_toggle", type="primary"):
            st.session_state.vocogni_assistant_open = not st.session_state.vocogni_assistant_open
            st.rerun()

    if not st.session_state.vocogni_assistant_open:
        return

    with st.container(key="vocogni_assistant_panel", border=True):
        title_col, close_col = st.columns([5, 1], vertical_alignment="center")
        with title_col:
            st.markdown("### Vocogni Study Guide")
            st.caption("Saved-learning tools plus optional AI tutoring")
        with close_col:
            if st.button("✕", key="vocogni_assistant_close", help="Close Study Guide"):
                st.session_state.vocogni_assistant_open = False
                st.rerun()

        if not provider_ready:
            st.session_state.vocogni_ai_opt_in = False

        ai_enabled = st.checkbox(
            "Enable external AI tutoring for this session",
            key="vocogni_ai_opt_in",
            disabled=not provider_ready,
        )
        if provider_ready:
            st.caption(
                "When enabled, open-ended questions are sent to the configured provider "
                "with up to 8 messages from previous AI-tutoring turns and a limited learning summary. "
                "The summary may include grade level, learning preferences, course accuracy, and mistake tags. "
                "Local profile/notes/progress-summary replies are excluded from chat history."
            )
        else:
            st.warning(
                "AI provider is not configured. Local Study Guide commands still work. "
                "Configure VOCogni_LLM_BASE_URL, VOCogni_LLM_MODEL, and VOCogni_LLM_API_KEY "
                "or add an [llm] section to Streamlit secrets to enable AI tutoring."
            )

        st.caption(
            "External AI is off by default. If enabled, your current message and selected prior AI chat "
            "messages are sent to the configured provider. Do not enter passwords, contact details, "
            "precise location, or sensitive information. Provider retention and training terms "
            "depend on the provider you configure."
        )

        if st.button(
            "Read Terms, Privacy & AI Safety",
            key="vocogni_assistant_policy_button",
            use_container_width=True,
        ):
            st.session_state.nav = "Settings"
            st.session_state.vocogni_assistant_open = False
            st.rerun()

        messages = st.session_state.vocogni_assistant_messages
        if not isinstance(messages, list):
            messages = []
            st.session_state.vocogni_assistant_messages = messages

        quick_request = None
        with st.container(key="vocogni_assistant_quick_requests"):
            st.markdown("**Quick requests**")
            st.caption("These account-data shortcuts run locally and do not require external AI.")
            quick_col1, quick_col2 = st.columns(2, gap="small")
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

        for message in messages[-8:]:
            role = message.get("role", "assistant")
            if role not in {"user", "assistant"}:
                continue
            with st.chat_message(role):
                st.markdown(str(message.get("content", "")))
                if role == "assistant" and message.get("mode") == "llm":
                    st.caption("AI-generated response · Check important answers against trusted course materials.")
                elif role == "assistant" and message.get("mode") == "fallback":
                    st.caption("Local fallback response")

        with st.form("vocogni_assistant_form", clear_on_submit=True):
            query = st.text_input(
                "Message",
                placeholder="Ask a subject question or request a progress summary",
                label_visibility="collapsed",
                max_chars=1200,
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
                mode = "local"

                if _is_unhandled(reply, route):
                    if ai_enabled and provider_ready:
                        history = _recent_ai_history(messages[:-1])
                        result = generate_ai_answer(
                            chosen_query,
                            history=history,
                            learner_context=_learner_context(profile, progress),
                            llm_config=provider_config,
                        )
                        reply = result["text"]
                        mode = result.get("mode", "fallback")
                    else:
                        reply = (
                            "I can handle saved-profile, progress, mistake, course, and navigation "
                            "requests locally. For open-ended subject tutoring, configure an AI provider "
                            "and enable external AI tutoring above. The AI option is off by default."
                        )
                        mode = "local"

                reply = reply.replace(
                    "The Study Guide is rule-based and does not call a generative AI model in this build.",
                    "The Study Guide has local rule-based commands and optional external AI tutoring, "
                    "which is off by default and requires session opt-in.",
                )
                reply = reply.replace(
                    "The Study Guide uses data already in Vocogni. It does not infer missing results or invent a learning history.",
                    "Local commands use saved Vocogni data. Optional AI tutoring uses only a limited learning summary "
                    "and selected prior AI chat context when you enable it.",
                )

                messages.append({"role": "assistant", "content": reply, "mode": mode})
                st.session_state.vocogni_assistant_messages = messages[-20:]
                if route:
                    st.session_state.nav = route
                    st.session_state.vocogni_assistant_open = False
                st.rerun()
