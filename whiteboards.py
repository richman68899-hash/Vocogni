"""Public whiteboard data helpers used by the UI and persistence boundary."""
from __future__ import annotations

from typing import Any

import whiteboard_data


def create_board(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return whiteboard_data.create_board(*args, **kwargs)


def create_page(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return whiteboard_data.create_page(*args, **kwargs)


def sanitize_board(value: Any) -> dict[str, Any] | None:
    """Validate one browser-originated board; invalid input returns None."""
    boards = whiteboard_data.sanitize_boards([value])
    return boards[0] if boards else None


def sanitize_boards(value: Any) -> list[dict[str, Any]]:
    return whiteboard_data.sanitize_boards(value)


def sanitize_page(value: Any) -> dict[str, Any] | None:
    return whiteboard_data.sanitize_page(value)


def page_to_svg(value: Any) -> str:
    return whiteboard_data.page_to_svg(value)
