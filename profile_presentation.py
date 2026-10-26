"""Pure presentation helpers for Vocogni's learner profile.

Kept independent of Streamlit so escaping, icon markup, and avatar initials
can be tested in the lightweight unit-test environment.
"""

from __future__ import annotations

import html
from typing import Any


def display_profile_value(value: Any) -> str:
    """Format a profile value as safe text for an HTML fragment."""
    if value is None:
        text = "Not specified"
    elif isinstance(value, list):
        text = ", ".join(str(item) for item in value) if value else "Not specified"
    else:
        text = str(value).strip() or "Not specified"
    return html.escape(text)


def profile_icon_svg(name: str) -> str:
    """Return a small, consistent, decorative line icon for profile sections."""
    icons = {
        "user": (
            '<circle cx="12" cy="8" r="3.5"/>'
            '<path d="M5 20c.6-3.2 3-5 7-5s6.4 1.8 7 5"/>'
        ),
        "book": (
            '<path d="M3.5 5.5A2.5 2.5 0 0 1 6 3h5v17H6a2.5 2.5 0 0 0-2.5 2z"/>'
            '<path d="M20.5 5.5A2.5 2.5 0 0 0 18 3h-5v17h5a2.5 2.5 0 0 1 2.5 2z"/>'
        ),
        "target": (
            '<circle cx="12" cy="12" r="8.5"/>'
            '<circle cx="12" cy="12" r="4.8"/>'
            '<circle cx="12" cy="12" r="1.3"/>'
        ),
        "spark": (
            '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>'
            '<path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/>'
        ),
        "shield": (
            '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>'
            '<path d="m9 12 2 2 4-4"/>'
        ),
    }
    paths = icons.get(name, icons["spark"])
    return (
        '<svg class="vc-profile-icon-art" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">'
        + paths + '</svg>'
    )


def profile_initials(name: Any) -> str:
    """Create a stable, privacy-light avatar monogram from the display name."""
    clean = str(name or "").strip()
    if not clean:
        return "L"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return clean[:1].upper()
