"""Render Vocogni's version-controlled legal and safety notices.

The documents are kept in docs/legal so the in-app copies and repository copies
share a single source of truth. These drafts must be completed and reviewed
before the service is treated as ready for public launch.
"""
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
        "- Sign out on shared devices and avoid adding sensitive personal details.\n"
        "- The final privacy contact, retention period, and deletion process are not configured yet.\n"
        "- Child-facing use is not cleared until required reviews and safeguards are completed."
    ),
    "ai_safety": (
        "**Quick read**\n\n"
        "- The Study Guide uses preset rules; it is not a generative AI chatbot.\n"
        "- Check important answers and ask a teacher if something seems wrong.\n"
        "- Do not enter passwords or private details about yourself or classmates.\n"
        "- The app is not watched live and cannot promise to detect every unsafe situation.\n"
        "- A monitored safety contact and child-safety review are still outstanding."
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
