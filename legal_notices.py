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
            st.markdown(load_notice(name))
