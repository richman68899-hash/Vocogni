"""Private whiteboard document model and validation for Vocogni Notes.

The model is deliberately plain JSON so boards can be saved inside the existing
learner state bundle. No executable HTML, uploaded assets, or external content
are stored in the first release.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


PALETTE = {
    "Red": "#D94A4A",
    "Orange": "#E58A32",
    "Yellow": "#D9B52B",
    "Green": "#399568",
    "Cyan": "#2BA6B4",
    "Blue": "#477ED1",
    "Pink": "#D66D9B",
    "Purple": "#8D6BC1",
    "Grey": "#858B95",
    "System": None,
}
DEFAULT_COLORS = ("#1D2730", "#2563EB", "#D94A4A", "#399568", "#E58A32", "#8D6BC1")
BACKGROUNDS = ("blank", "dots", "grid", "ruled", "coordinate")
BACKGROUND_LABELS = {
    "blank": "Blank",
    "dots": "Dot grid",
    "grid": "Graph paper",
    "ruled": "Ruled",
    "coordinate": "Coordinate plane",
}
OBJECT_TYPES = ("stroke", "shape", "text", "sticky")
SHAPE_TYPES = ("rectangle", "ellipse", "triangle", "line", "arrow")
MAX_WHITEBOARDS = 100
MAX_PAGES = 30
MAX_OBJECTS_PER_PAGE = 1500
MAX_OBJECTS_PER_BOARD = 5000
MAX_POINTS_PER_STROKE = 5000
MAX_BOARD_BYTES = 4 * 1024 * 1024
MAX_BOARD_TITLE_LENGTH = 120
MAX_OBJECT_TEXT_LENGTH = 12000
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _string(value: Any, default: str = "", maximum: int = 1000) -> str:
    if not isinstance(value, str):
        return default
    return value.strip()[:maximum]


def _identifier(value: Any, default: str) -> str:
    candidate = _string(value, default, 100)
    return candidate if _ID_PATTERN.fullmatch(candidate) else default


def _number(value: Any, default: float = 0.0, minimum: float = -100000.0,
            maximum: float = 100000.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return min(max(number, minimum), maximum)


def _positive_int(value: Any, default: int = 1, maximum: int = 1000000) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return default
    return min(value, maximum)


def _color(value: Any, default: str = "#2563EB") -> str:
    if isinstance(value, str) and _HEX_COLOR.fullmatch(value):
        return value.upper()
    return default


def _normalize_points(value: Any) -> list[list[float]]:
    if not isinstance(value, list):
        return []
    points = []
    for point in value[:MAX_POINTS_PER_STROKE]:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        points.append([
            _number(point[0], 0.0, -10000, 10000),
            _number(point[1], 0.0, -10000, 10000),
        ])
    return points


def _sanitize_object(raw: Any, fallback_id: str) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    kind = raw.get("type")
    if kind not in OBJECT_TYPES:
        return None

    object_id = _identifier(raw.get("id"), fallback_id)
    color = _color(raw.get("color"))
    width = _number(raw.get("width"), 3.0, 0.5, 40.0)
    x = _number(raw.get("x"), 0.0, -10000, 10000)
    y = _number(raw.get("y"), 0.0, -10000, 10000)

    if kind == "stroke":
        points = _normalize_points(raw.get("points"))
        if not points:
            return None
        return {
            "id": object_id,
            "type": "stroke",
            "points": points,
            "color": color,
            "width": width,
            "opacity": _number(raw.get("opacity"), 1.0, 0.05, 1.0),
        }

    if kind == "shape":
        shape = raw.get("shape")
        if shape not in SHAPE_TYPES:
            return None
        return {
            "id": object_id,
            "type": "shape",
            "shape": shape,
            "x": x,
            "y": y,
            "width": _number(raw.get("width"), 100.0, -10000, 10000),
            "height": _number(raw.get("height"), 70.0, -10000, 10000),
            "color": color,
            "fill": _color(raw.get("fill"), "#FFFFFF"),
            "filled": bool(raw.get("filled", False)),
            "stroke_width": _number(raw.get("stroke_width", width), 1.0, 0.5, 40.0),
        }

    if kind == "text":
        text = _string(raw.get("text"), "", MAX_OBJECT_TEXT_LENGTH)
        if not text:
            return None
        return {
            "id": object_id,
            "type": "text",
            "x": x,
            "y": y,
            "text": text,
            "color": color,
            "font_size": _number(raw.get("font_size"), 28.0, 8.0, 160.0),
        }

    text = _string(raw.get("text"), "Sticky note", MAX_OBJECT_TEXT_LENGTH)
    if not text:
        text = "Sticky note"
    return {
        "id": object_id,
        "type": "sticky",
        "x": x,
        "y": y,
        "width": _number(raw.get("width"), 220.0, 40.0, 3000.0),
        "height": _number(raw.get("height"), 150.0, 40.0, 3000.0),
        "text": text,
        "color": _color(raw.get("color"), "#FFF2A8"),
        "text_color": _color(raw.get("text_color"), "#303238"),
        "font_size": _number(raw.get("font_size"), 20.0, 8.0, 100.0),
    }


def _sanitize_page(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    page_id = _identifier(raw.get("id"), f"page_{index}")
    background = raw.get("background")
    if background not in BACKGROUNDS:
        background = "blank"
    objects = []
    raw_objects = raw.get("objects", [])
    seen = set()
    if isinstance(raw_objects, list):
        for obj_index, raw_object in enumerate(raw_objects[:MAX_OBJECTS_PER_PAGE]):
            object_id = _identifier(
                raw_object.get("id") if isinstance(raw_object, dict) else None,
                f"object_{index}_{obj_index + 1}",
            )
            if object_id in seen:
                object_id = f"{object_id}_{obj_index + 1}"
            seen.add(object_id)
            obj = _sanitize_object(raw_object, object_id)
            if obj:
                objects.append(obj)
    return {
        "id": page_id,
        "title": _string(raw.get("title"), f"Page {index}", 80) or f"Page {index}",
        "background": background,
        "objects": objects,
    }


def sanitize_board(raw: Any, *, default_id: str = "board_1") -> dict[str, Any]:
    """Validate an untrusted board document and return a bounded plain-JSON copy."""
    if not isinstance(raw, dict):
        raise ValueError("The whiteboard data must be an object.")

    board_id = _identifier(raw.get("id"), default_id)
    title = _string(raw.get("title"), "Untitled whiteboard", MAX_BOARD_TITLE_LENGTH)
    title = title or "Untitled whiteboard"
    folder_id = raw.get("folder_id")
    if isinstance(folder_id, bool) or not isinstance(folder_id, int) or folder_id < 1:
        folder_id = None

    pages_raw = raw.get("pages")
    if not isinstance(pages_raw, list):
        pages_raw = []
    pages_raw = pages_raw[:MAX_PAGES]
    pages = [_sanitize_page(page, index + 1) for index, page in enumerate(pages_raw)]
    if not pages:
        pages = [{"id": "page_1", "title": "Page 1", "background": "blank", "objects": []}]

    page_ids = set()
    for index, page in enumerate(pages, start=1):
        if page["id"] in page_ids:
            page["id"] = f"page_{index}_{index}"
        page_ids.add(page["id"])

    total_objects = sum(len(page["objects"]) for page in pages)
    if total_objects > MAX_OBJECTS_PER_BOARD:
        raise ValueError(
            f"This board has too many objects ({total_objects}). "
            f"The current limit is {MAX_OBJECTS_PER_BOARD} per board."
        )

    active_page_id = raw.get("active_page_id")
    if active_page_id not in page_ids:
        active_page_id = pages[0]["id"]

    created_at = _string(raw.get("created_at"), "", 80)
    updated_at = _string(raw.get("updated_at"), "", 80)
    document = {
        "id": board_id,
        "title": title,
        "folder_id": folder_id,
        "pages": pages,
        "active_page_id": active_page_id,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    serialized = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > MAX_BOARD_BYTES:
        raise ValueError(
            "This board is too large to save safely. Reduce the number of objects "
            "or long text blocks, then try again."
        )
    return document


def sanitize_whiteboards(saved: Any) -> list[dict[str, Any]]:
    """Restore valid boards; skip malformed or oversized entries instead of crashing."""
    if not isinstance(saved, list):
        return []
    cleaned = []
    seen_ids = set()
    for index, raw in enumerate(saved[:MAX_WHITEBOARDS]):
        if not isinstance(raw, dict):
            continue
        fallback_id = f"board_{index + 1}"
        try:
            board = sanitize_board(raw, default_id=fallback_id)
        except (ValueError, TypeError):
            continue
        if board["id"] in seen_ids:
            board["id"] = f"{board['id']}_{index + 1}"
        seen_ids.add(board["id"])
        cleaned.append(board)
    return cleaned


def next_whiteboard_id(boards: list[dict[str, Any]]) -> int:
    values = []
    for board in boards:
        if not isinstance(board, dict):
            continue
        board_id = board.get("id")
        match = re.fullmatch(r"board_(\d+)", str(board_id))
        if match:
            values.append(int(match.group(1)))
    return max(values, default=0) + 1


def create_whiteboard(
    board_id: int,
    title: str = "Untitled whiteboard",
    folder_id: int | None = None,
    now: str | None = None,
    template: str = "grid",
) -> dict[str, Any]:
    """Create a blank board or a lightweight study template."""
    timestamp = now or now_utc()
    if template not in {"blank", "dots", "grid", "ruled", "coordinate", "mind_map", "flowchart"}:
        template = "grid"

    objects = []
    background = template if template in BACKGROUNDS else "grid"
    if template == "mind_map":
        background = "blank"
        objects = [
            {"id": "connector_left_top", "type": "shape", "shape": "line", "x": 600, "y": 380, "width": -300, "height": -160, "color": "#AAB7C0", "stroke_width": 2},
            {"id": "connector_right_top", "type": "shape", "shape": "line", "x": 600, "y": 380, "width": 300, "height": -160, "color": "#AAB7C0", "stroke_width": 2},
            {"id": "connector_left_bottom", "type": "shape", "shape": "line", "x": 600, "y": 380, "width": -300, "height": 160, "color": "#AAB7C0", "stroke_width": 2},
            {"id": "connector_right_bottom", "type": "shape", "shape": "line", "x": 600, "y": 380, "width": 300, "height": 160, "color": "#AAB7C0", "stroke_width": 2},
            {"id": "center", "type": "shape", "shape": "ellipse", "x": 500, "y": 330, "width": 200, "height": 100, "color": "#477ED1", "fill": "#EAF2FF", "filled": True, "stroke_width": 2},
            {"id": "center_text", "type": "text", "x": 540, "y": 385, "text": "Main idea", "color": "#244B86", "font_size": 24},
            {"id": "topic_left_top", "type": "shape", "shape": "rectangle", "x": 150, "y": 150, "width": 180, "height": 76, "color": "#399568", "fill": "#E9F7EF", "filled": True, "stroke_width": 2},
            {"id": "topic_right_top", "type": "shape", "shape": "rectangle", "x": 870, "y": 150, "width": 180, "height": 76, "color": "#E58A32", "fill": "#FFF3E5", "filled": True, "stroke_width": 2},
            {"id": "topic_left_bottom", "type": "shape", "shape": "rectangle", "x": 150, "y": 530, "width": 180, "height": 76, "color": "#8D6BC1", "fill": "#F4EEFC", "filled": True, "stroke_width": 2},
            {"id": "topic_right_bottom", "type": "shape", "shape": "rectangle", "x": 870, "y": 530, "width": 180, "height": 76, "color": "#D66D9B", "fill": "#FCEEF4", "filled": True, "stroke_width": 2},
            {"id": "label_left_top", "type": "text", "x": 178, "y": 195, "text": "Branch 1", "color": "#245A43", "font_size": 20},
            {"id": "label_right_top", "type": "text", "x": 896, "y": 195, "text": "Branch 2", "color": "#8B4F12", "font_size": 20},
            {"id": "label_left_bottom", "type": "text", "x": 178, "y": 575, "text": "Branch 3", "color": "#5D4383", "font_size": 20},
            {"id": "label_right_bottom", "type": "text", "x": 896, "y": 575, "text": "Branch 4", "color": "#963D69", "font_size": 20},
        ]
    elif template == "flowchart":
        background = "blank"
        objects = [
            {"id": "start_shape", "type": "shape", "shape": "rectangle", "x": 460, "y": 55, "width": 280, "height": 76, "color": "#399568", "fill": "#E9F7EF", "filled": True, "stroke_width": 2},
            {"id": "start_label", "type": "text", "x": 545, "y": 101, "text": "Start / Input", "color": "#245A43", "font_size": 22},
            {"id": "arrow_one", "type": "shape", "shape": "arrow", "x": 600, "y": 132, "width": 0, "height": 70, "color": "#667985", "stroke_width": 2},
            {"id": "process_shape", "type": "shape", "shape": "rectangle", "x": 460, "y": 205, "width": 280, "height": 76, "color": "#477ED1", "fill": "#EAF2FF", "filled": True, "stroke_width": 2},
            {"id": "process_label", "type": "text", "x": 535, "y": 250, "text": "Process", "color": "#244B86", "font_size": 22},
            {"id": "arrow_two", "type": "shape", "shape": "arrow", "x": 600, "y": 282, "width": 0, "height": 70, "color": "#667985", "stroke_width": 2},
            {"id": "decision_shape", "type": "shape", "shape": "rectangle", "x": 460, "y": 355, "width": 280, "height": 76, "color": "#E58A32", "fill": "#FFF3E5", "filled": True, "stroke_width": 2},
            {"id": "decision_label", "type": "text", "x": 520, "y": 400, "text": "Decision / Output", "color": "#8B4F12", "font_size": 21},
            {"id": "arrow_three", "type": "shape", "shape": "arrow", "x": 600, "y": 432, "width": 0, "height": 70, "color": "#667985", "stroke_width": 2},
            {"id": "end_shape", "type": "shape", "shape": "rectangle", "x": 460, "y": 505, "width": 280, "height": 76, "color": "#8D6BC1", "fill": "#F4EEFC", "filled": True, "stroke_width": 2},
            {"id": "end_label", "type": "text", "x": 555, "y": 550, "text": "End / Result", "color": "#5D4383", "font_size": 22},
        ]

    return sanitize_board({
        "id": f"board_{_positive_int(board_id)}",
        "title": title,
        "folder_id": folder_id,
        "pages": [{
            "id": "page_1",
            "title": "Page 1",
            "background": background,
            "objects": objects,
        }],
        "active_page_id": "page_1",
        "created_at": timestamp,
        "updated_at": timestamp,
    })


def duplicate_whiteboard(
    board: dict[str, Any],
    new_id: int,
    title: str | None = None,
) -> dict[str, Any]:
    """Duplicate a board while assigning fresh page and object identifiers."""
    from copy import deepcopy

    copied = deepcopy(board)
    copied["id"] = f"board_{_positive_int(new_id)}"
    copied["title"] = _string(title, str(board.get("title", "Whiteboard")) + " copy", MAX_BOARD_TITLE_LENGTH)
    copied["created_at"] = now_utc()
    copied["updated_at"] = copied["created_at"]
    for page_index, page in enumerate(copied.get("pages", []), start=1):
        page["id"] = f"page_{page_index}"
        for object_index, obj in enumerate(page.get("objects", []), start=1):
            obj["id"] = f"object_{page_index}_{object_index}"
    copied["active_page_id"] = copied["pages"][0]["id"] if copied.get("pages") else "page_1"
    return sanitize_board(copied)
def update_whiteboard_metadata(
    board: dict[str, Any],
    *,
    title: str,
    folder_id: int | None,
) -> dict[str, Any]:
    clean_title = _string(title, "", MAX_BOARD_TITLE_LENGTH)
    if not clean_title:
        raise ValueError("Whiteboard title cannot be empty.")
    if folder_id is not None and (
        isinstance(folder_id, bool) or not isinstance(folder_id, int) or folder_id < 1
    ):
        raise ValueError("Choose a valid folder.")
    board["title"] = clean_title
    board["folder_id"] = folder_id
    board["updated_at"] = now_utc()
    return board


def board_object_counts(board: dict[str, Any]) -> tuple[int, int]:
    pages = board.get("pages", [])
    return len(pages), sum(len(page.get("objects", [])) for page in pages)
