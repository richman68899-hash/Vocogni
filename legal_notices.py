"""Render Vocogni's version-controlled legal and safety notices."""
from __future__ import annotations

from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parent
NOTICE_FILES = {
    "terms": ("Terms of Use (prototype draft)", _ROOT / "docs" / "legal" / "terms-of-service.md"),
    "privacy": ("Privacy Notice (prototype draft)", _ROOT / "docs" / "legal" / "privacy-notice.md"),
    "ai_safety": ("AI Use and Safety Notes", _ROOT / "docs" / "legal" / "ai-use-and-safety.md"),
}

DRAFT_NOTICE = (
    "Prototype draft only. These notices are not final public legal terms: "
    "the operator identity, monitored contact details, data-retention and deletion "
    "processes, and legal review must be completed before public launch."
)

NOTICE_SUMMARIES = {
    "terms": (
        "**Quick read**\n\n"
        "- Vocogni is a learning prototype, not an official school assessment.\n"
        "- Check important answers with your teacher or course materials.\n"
        "- The rules and contact details are still being completed.\n"
        "- Do not treat this draft as final permission or proof of legal compliance."
    ),
    "privacy": (
        "**Quick read**\n\n"
        "- Vocogni saves learning progress and details you choose to enter.\n"
        "- Optional AI tutoring sends your prompt, recent chat context, and a limited learning summary to the configured provider only after session opt-in.\n"
        "- Your name, email, saved notes, milestones, and account ID are not added to the AI context summary.\n"
        "- Provider retention, training, and data location depend on the provider and must be reviewed.\n"
        "- Child-facing use is not cleared until required reviews and safeguards are completed."
    ),
    "ai_safety": (
        "**Quick read**\n\n"
        "- Local Study Guide commands work without generative AI.\n"
        "- Open-ended AI tutoring is optional, off by default, and requires session opt-in.\n"
        "- When enabled, your message, up to 8 messages from prior AI-tutoring turns; local account-data summaries are excluded, and a limited learning summary are sent to the configured external provider.\n"
        "- AI can make mistakes. Check important answers with trusted course materials or a teacher.\n"
        "- Do not enter passwords, contact details, precise location, or sensitive information.\n"
        "- The app is not watched live; a monitored safety contact and child-safety review are still outstanding."
    ),
}


def load_notice(name: str) -> str:
    """Load one approved notice by stable key; reject unknown keys."""
    if name not in NOTICE_FILES:
        raise KeyError(f"Unknown legal notice: {name}")
    _title, path = NOTICE_FILES[name]
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Legal notice file is unavailable: {path.name}") from exc


def render_legal_notices(st: Any, compact: bool = False) -> None:
    """Render collapsed notices for easy access from login and Settings."""
    if compact:
        st.caption(DRAFT_NOTICE)
    else:
        st.info(DRAFT_NOTICE)

    for name in ("terms", "privacy", "ai_safety"):
        title, _path = NOTICE_FILES[name]
        with st.expander(title, expanded=False):
            st.markdown(NOTICE_SUMMARIES[name])
            st.markdown("---")
            st.markdown(load_notice(name))
