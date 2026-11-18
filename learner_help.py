"""Progressive, deterministic help for verified practice questions.

The helper reuses authored lesson material and reviewed mistake guidance. It
never calls an AI provider, grades an answer, or reads the question's answer
or solution explanation. Independent-transfer items remain hint-free.
"""
from __future__ import annotations

from typing import Any

import feedback_guidance


def _clean_text(value: Any) -> str:
    """Return non-empty authored text without coercing arbitrary objects."""
    return value.strip() if isinstance(value, str) else ""


def build_help_ladder(
    question: Any,
    lesson: Any,
    *,
    verification_status: str,
) -> dict[str, Any]:
    """Build ordered help steps for a verified, non-transfer practice item.

    The returned steps progressively reveal an existing cue, a key principle,
    a next action, and (when available) a related worked example. No answer,
    question solution explanation, or grading result is included.
    """
    if not isinstance(question, dict) or not isinstance(lesson, dict):
        return {"available": False, "reason": "invalid_content", "focus": "", "steps": []}

    if question.get("_is_transfer_check") or question.get("evidence_type") == "independent_transfer":
        return {"available": False, "reason": "independent_transfer", "focus": "", "steps": []}

    if verification_status != "verified":
        return {"available": False, "reason": "unverified_content", "focus": "", "steps": []}

    focus = (
        _clean_text(question.get("skill_tag"))
        or _clean_text(question.get("skill"))
        or _clean_text(question.get("mistake_tag"))
        or _clean_text(lesson.get("title"))
    )

    steps: list[dict[str, str]] = []
    seen: set[str] = set()

    def add_step(label: str, content: Any) -> None:
        value = _clean_text(content)
        normalized = " ".join(value.split()).casefold()
        if not value or normalized in seen:
            return
        seen.add(normalized)
        steps.append({"label": label, "content": value})

    # A question-authored cue is the least revealing first step.
    add_step("First cue", question.get("input_hint") or question.get("hint"))

    guidance = feedback_guidance.build_feedback_guidance(question)
    if guidance:
        add_step("Key idea", guidance.get("likely_issue"))
        add_step("Try this next", guidance.get("next_step"))
        add_step("Similar worked example", guidance.get("worked_example"))

    # Generic lesson text is the fallback, not invented guidance. Keep adding
    # authored lesson material until the ladder has a useful example step.
    if len(steps) < 3:
        add_step("Review the core idea", lesson.get("explanation"))
        add_step("Compare a worked example", lesson.get("worked_example"))

    return {
        "available": bool(steps),
        "reason": None if steps else "no_authored_support",
        "focus": focus,
        "steps": steps,
    }


__all__ = ["build_help_ladder"]
