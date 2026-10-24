"""Safe, framework-free data helpers for the Notes whiteboard.

The whiteboard stores editable vector objects in the existing learner JSON bundle.
This module intentionally validates browser-originated data before persistence.
"""
from __future__ import annotations

from copy import deepcopy
from html import escape
import math
import re
from typing import Any
from uuid import uuid4

MAX_BOARDS = 100
MAX_PAGES_PER_BOARD = 40
MAX_OBJECTS_PER_PAGE = 200
MAX_POINTS_PER_STROKE = 2000
MAX_POINTS_PER_PAGE = 20000
MAX_TEXT_LENGTH = 5000
MAX_OBJECTS_PER_BOARD = 1200
MAX_POINTS_PER_BOARD = 30000
MAX_TEXT_CHARS_PER_PAGE = 20000
MAX_TEXT_CHARS_PER_BOARD = 100000
BACKGROUNDS = {"plain", "grid", "dots", "dark"}
OBJECT_TYPES = {"stroke", "shape", "text", "sticky"}
SHAPES = {"rect", "ellipse", "triangle", "line", "arrow"}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def new_id() -> str:
    """Return a collision-resistant ID suitable for saved UI objects."""
    return uuid4().hex


def _number(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return max(-10000.0, min(10000.0, result))
    except (TypeError, ValueError, OverflowError):
        pass
    return default


def _color(value: Any, default: str = "#273142") -> str:
    return value if isinstance(value, str) and HEX_COLOR.fullmatch(value) else default


def create_page(title: str = "Page 1", background: str = "grid") -> dict[str, Any]:
    """Create an empty page with stable dimensions and a safe background."""
    return {
        "id": new_id(),
        "title": (str(title).strip() or "Page 1")[:80],
        "width": 1200,
        "height": 800,
        "background": background if background in BACKGROUNDS else "grid",
        "objects": [],
    }


def create_board(
    board_id: str | None = None,
    title: str = "Untitled whiteboard",
    folder_id: Any = None,
    template: str = "Blank",
) -> dict[str, Any]:
    """Create a whiteboard with one page and optional learning template."""
    templates = {
        "Blank": ("plain", []),
        "Graph paper": ("grid", []),
        "Coordinate plane": ("grid", [
            {"id": new_id(), "type": "shape", "shape": "line", "x": 40, "y": 400,
             "w": 1120, "h": 0, "color": "#6B7280", "width": 2},
            {"id": new_id(), "type": "shape", "shape": "arrow", "x": 600, "y": 750,
             "w": 0, "h": -700, "color": "#6B7280", "width": 2},
        ]),
        "Mind map": ("plain", [
            {"id": new_id(), "type": "sticky", "x": 450, "y": 310, "w": 300, "h": 150,
             "text": "Central idea", "color": "#F8E7A1"},
            {"id": new_id(), "type": "text", "x": 470, "y": 480,
             "text": "Add branches around this idea", "color": "#525866", "fontSize": 20},
        ]),
        "Flowchart": ("plain", [
            {"id": new_id(), "type": "shape", "shape": "rect", "x": 450, "y": 70,
             "w": 300, "h": 90, "color": "#477ED1", "width": 3},
            {"id": new_id(), "type": "text", "x": 530, "y": 105,
             "text": "Start", "color": "#273142", "fontSize": 28},
            {"id": new_id(), "type": "shape", "shape": "arrow", "x": 600, "y": 165,
             "w": 0, "h": 90, "color": "#6B7280", "width": 3},
            {"id": new_id(), "type": "shape", "shape": "rect", "x": 450, "y": 260,
             "w": 300, "h": 90, "color": "#399568", "width": 3},
            {"id": new_id(), "type": "text", "x": 500, "y": 295,
             "text": "Process", "color": "#273142", "fontSize": 28},
        ]),
    }
    background, objects = templates.get(template, templates["Blank"])
    page = create_page("Page 1", background)
    page["objects"] = deepcopy(objects)
    return {
        "id": board_id or new_id(),
        "title": (str(title).strip() or "Untitled whiteboard")[:100],
        "folder_id": folder_id if isinstance(folder_id, int) and not isinstance(folder_id, bool) else None,
        "created_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pages": [page],
    }


def sanitize_page(
    value: Any,
    *,
    max_objects: int = MAX_OBJECTS_PER_PAGE,
    max_points: int = MAX_POINTS_PER_STROKE,
    max_text_chars: int = MAX_TEXT_CHARS_PER_PAGE,
) -> dict[str, Any] | None:
    """Validate one bounded page before it enters persistent learner state."""
    if not isinstance(value, dict):
        return None
    page_id = value.get("id")
    if not isinstance(page_id, str) or not page_id or len(page_id) > 100:
        page_id = new_id()
    background = value.get("background", "grid")
    if background not in BACKGROUNDS:
        background = "grid"
    object_limit = max(0, min(MAX_OBJECTS_PER_PAGE, int(max_objects)))
    point_budget = max(0, min(MAX_POINTS_PER_PAGE, int(max_points)))
    text_budget = max(0, min(MAX_TEXT_CHARS_PER_PAGE, int(max_text_chars)))
    objects = []
    remaining_points = point_budget
    remaining_text = text_budget
    source_objects = value.get("objects", [])
    if isinstance(source_objects, list):
        for raw in source_objects[:object_limit]:
            if not isinstance(raw, dict) or raw.get("type") not in OBJECT_TYPES:
                continue
            kind = raw["type"]
            item = {"id": str(raw.get("id") or new_id())[:100], "type": kind}
            if kind == "stroke":
                points_raw = raw.get("points", [])
                points = []
                point_limit = min(MAX_POINTS_PER_STROKE, remaining_points)
                if isinstance(points_raw, list):
                    for point in points_raw[:point_limit]:
                        if isinstance(point, dict):
                            points.append({"x": _number(point.get("x")), "y": _number(point.get("y"))})
                if len(points) < 2:
                    continue
                remaining_points -= len(points)
                item.update({
                    "points": points,
                    "color": _color(raw.get("color")),
                    "width": max(1.0, min(48.0, _number(raw.get("width"), 4.0))),
                    "tool": raw.get("tool") if raw.get("tool") in {"pen", "highlighter"} else "pen",
                })
            elif kind == "shape":
                shape = raw.get("shape")
                if shape not in SHAPES:
                    continue
                item.update({
                    "shape": shape, "x": _number(raw.get("x")), "y": _number(raw.get("y")),
                    "w": _number(raw.get("w")), "h": _number(raw.get("h")),
                    "color": _color(raw.get("color")),
                    "width": max(1.0, min(48.0, _number(raw.get("width"), 3.0))),
                    "fill": _color(raw.get("fill"), "#FFFFFF"),
                })
            else:
                raw_text = raw.get("text", "")
                if not isinstance(raw_text, str):
                    raw_text = str(raw_text)
                text = raw_text[:min(MAX_TEXT_LENGTH, remaining_text)]
                remaining_text -= len(text)
                item.update({
                    "x": _number(raw.get("x")), "y": _number(raw.get("y")),
                    "text": text, "color": _color(raw.get("color")),
                    "fontSize": max(10.0, min(96.0, _number(raw.get("fontSize"), 24.0))),
                })
                if kind == "sticky":
                    item.update({
                        "w": max(100.0, min(800.0, _number(raw.get("w"), 220.0))),
                        "h": max(80.0, min(600.0, _number(raw.get("h"), 140.0))),
                        "color": _color(raw.get("color"), "#F8E7A1"),
                    })
            objects.append(item)
    return {
        "id": page_id,
        "title": str(value.get("title", "Page"))[:80] or "Page",
        "width": 1200,
        "height": 800,
        "background": background,
        "objects": objects,
    }


def sanitize_boards(value: Any) -> list[dict[str, Any]]:
    """Restore validated boards with aggregate object, stroke and text budgets."""
    if not isinstance(value, list):
        return []
    boards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in value[:MAX_BOARDS]:
        if not isinstance(raw, dict):
            continue
        board_id = raw.get("id")
        if not isinstance(board_id, str) or not board_id or len(board_id) > 100 or board_id in seen:
            continue
        seen.add(board_id)
        raw_pages = raw.get("pages", [])
        pages = []
        remaining_objects = MAX_OBJECTS_PER_BOARD
        remaining_points = MAX_POINTS_PER_BOARD
        remaining_text = MAX_TEXT_CHARS_PER_BOARD
        if isinstance(raw_pages, list):
            for raw_page in raw_pages[:MAX_PAGES_PER_BOARD]:
                page = sanitize_page(
                    raw_page,
                    max_objects=remaining_objects,
                    max_points=remaining_points,
                    max_text_chars=remaining_text,
                )
                if page is None:
                    continue
                pages.append(page)
                remaining_objects -= len(page["objects"])
                for obj in page["objects"]:
                    if obj.get("type") == "stroke":
                        remaining_points -= len(obj.get("points", []))
                    elif obj.get("type") in {"text", "sticky"}:
                        remaining_text -= len(obj.get("text", ""))
                if remaining_objects <= 0:
                    remaining_objects = 0
                if remaining_points <= 0:
                    remaining_points = 0
                if remaining_text <= 0:
                    remaining_text = 0
        if not pages:
            pages = [create_page()]
        folder_id = raw.get("folder_id")
        boards.append({
            "id": board_id,
            "title": str(raw.get("title", "Untitled whiteboard")).strip()[:100] or "Untitled whiteboard",
            "folder_id": folder_id if isinstance(folder_id, int) and not isinstance(folder_id, bool) else None,
            "created_at": str(raw.get("created_at", ""))[:30],
            "updated_at": str(raw.get("updated_at", ""))[:30],
            "pages": pages,
        })
    return boards


def page_to_svg(page_value: Any) -> str:
    """Export a sanitized page to portable SVG (vector strokes remain editable)."""
    page = sanitize_page(page_value) or create_page()
    bg = {"plain": "#FFFFFF", "grid": "#FFFFFF", "dots": "#FFFFFF", "dark": "#20242B"}[page["background"]]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">',
        f'<rect width="1200" height="800" fill="{bg}"/>',
    ]
    if page["background"] in {"grid", "dots"}:
        for x in range(0, 1201, 40):
            if page["background"] == "grid":
                parts.append(f'<path d="M{x} 0 V800" stroke="#E7EAF0" stroke-width="1"/>')
        for y in range(0, 801, 40):
            if page["background"] == "grid":
                parts.append(f'<path d="M0 {y} H1200" stroke="#E7EAF0" stroke-width="1"/>')
        if page["background"] == "dots":
            for x in range(20, 1200, 40):
                for y in range(20, 800, 40):
                    parts.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="#D7DBE3"/>')
    for obj in page["objects"]:
        color = obj.get("color", "#273142")
        width = obj.get("width", 3)
        if obj["type"] == "stroke":
            points = obj["points"]
            d = " ".join(("M" if i == 0 else "L") + f'{p["x"]:.2f} {p["y"]:.2f}' for i, p in enumerate(points))
            opacity = ' opacity="0.35"' if obj.get("tool") == "highlighter" else ""
            parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{opacity}/>')
        elif obj["type"] == "shape":
            x, y, w, h = (obj[k] for k in ("x", "y", "w", "h"))
            if obj["shape"] == "rect":
                left, top, rect_w, rect_h = min(x, x + w), min(y, y + h), abs(w), abs(h)
                parts.append(f'<rect x="{left}" y="{top}" width="{rect_w}" height="{rect_h}" fill="none" stroke="{color}" stroke-width="{width}"/>')
            elif obj["shape"] == "ellipse":
                parts.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{abs(w)/2}" ry="{abs(h)/2}" fill="none" stroke="{color}" stroke-width="{width}"/>')
            elif obj["shape"] == "triangle":
                parts.append(f'<path d="M{x+w/2} {y} L{x+w} {y+h} L{x} {y+h} Z" fill="none" stroke="{color}" stroke-width="{width}"/>')
            elif obj["shape"] == "arrow":
                parts.append(f'<path d="M{x} {y} L{x+w} {y+h}" fill="none" stroke="{color}" stroke-width="{width}"/>')
            else:
                parts.append(f'<path d="M{x} {y} L{x+w} {y+h}" fill="none" stroke="{color}" stroke-width="{width}"/>')
        elif obj["type"] == "sticky":
            parts.append(f'<rect x="{obj["x"]}" y="{obj["y"]}" width="{obj["w"]}" height="{obj["h"]}" rx="8" fill="{color}"/>')
            text_color = "#273142"
            for i, line in enumerate(obj["text"].splitlines() or [""]):
                parts.append(f'<text x="{obj["x"]+12}" y="{obj["y"]+30+i*24}" fill="{text_color}" font-size="20">{escape(line)}</text>')
        else:
            for i, line in enumerate(obj["text"].splitlines() or [""]):
                parts.append(f'<text x="{obj["x"]}" y="{obj["y"]+i*obj["fontSize"]*1.25}" fill="{color}" font-size="{obj["fontSize"]}">{escape(line)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
