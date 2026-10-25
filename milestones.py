"""Framework-free data helpers for Notes learning milestones."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Any


PALETTE = {
    "Red": "#B6534D",
    "Orange": "#B8793E",
    "Yellow": "#9A7A25",
    "Green": "#4D8069",
    "Cyan": "#397E87",
    "Blue": "#52769E",
    "Pink": "#A96782",
    "Purple": "#7B699D",
    "Grey": "#727F83",
    "System": None,
}

MILESTONE_SECTIONS = (
    "Maths",
    "Science",
    "Productivity",
    "Vocogni",
    "Health",
    "Personal",
    "Other",
)

MILESTONE_EMOJIS = (
    "🎯", "📐", "📚", "🧠", "💻", "🚀", "✅", "🌱",
    "🏃", "🧪", "✍️", "💡", "🏆", "🗓️", "⭐", "🎨",
)


def _normalize_date(value: Any) -> str:
    """Validate a date and return its stable YYYY-MM-DD representation."""
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip()).isoformat()
        except ValueError:
            pass
    raise ValueError("Choose a valid milestone end date.")


def next_milestone_id(milestones: list[dict[str, Any]]) -> int:
    """Return the next unused positive milestone ID."""
    ids = []
    for milestone in milestones:
        if not isinstance(milestone, dict):
            continue
        value = milestone.get("id")
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            ids.append(value)
    return max(ids, default=0) + 1


def sanitize_milestones(saved: Any) -> list[dict[str, Any]]:
    """Restore valid milestones while tolerating missing or old saved fields."""
    if not isinstance(saved, list):
        return []

    cleaned = []
    seen_ids = set()
    next_id = 1
    today = date.today().isoformat()

    for raw in saved:
        if not isinstance(raw, dict):
            continue

        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            continue

        raw_id = raw.get("id")
        if (
            not isinstance(raw_id, int)
            or isinstance(raw_id, bool)
            or raw_id < 1
            or raw_id in seen_ids
        ):
            while next_id in seen_ids:
                next_id += 1
            milestone_id = next_id
        else:
            milestone_id = raw_id
        seen_ids.add(milestone_id)
        next_id = max(next_id, milestone_id + 1)

        try:
            end_date = _normalize_date(raw.get("end_date"))
        except ValueError:
            end_date = today

        section = raw.get("section")
        if section not in MILESTONE_SECTIONS:
            section = "Other"

        color = raw.get("color")
        if color not in PALETTE:
            color = "Grey"

        emoji = raw.get("emoji")
        if emoji not in MILESTONE_EMOJIS:
            emoji = "🎯"

        raw_items = raw.get("checklist", [])
        checklist = []
        seen_item_ids = set()
        next_item_id = 1
        if isinstance(raw_items, list):
            for raw_item in raw_items:
                if not isinstance(raw_item, dict):
                    continue
                text = raw_item.get("text")
                if not isinstance(text, str) or not text.strip():
                    continue

                raw_item_id = raw_item.get("id")
                if (
                    not isinstance(raw_item_id, int)
                    or isinstance(raw_item_id, bool)
                    or raw_item_id < 1
                    or raw_item_id in seen_item_ids
                ):
                    while next_item_id in seen_item_ids:
                        next_item_id += 1
                    item_id = next_item_id
                else:
                    item_id = raw_item_id
                seen_item_ids.add(item_id)
                next_item_id = max(next_item_id, item_id + 1)

                checklist.append({
                    "id": item_id,
                    "text": text.strip(),
                    "done": bool(raw_item.get("done", False)),
                })

        cleaned.append({
            "id": milestone_id,
            "title": title.strip(),
            "end_date": end_date,
            "section": section,
            "color": color,
            "emoji": emoji,
            "checklist": checklist,
            "next_item_id": max(
                next_item_id,
                int(raw.get("next_item_id", 1))
                if isinstance(raw.get("next_item_id"), int)
                and not isinstance(raw.get("next_item_id"), bool)
                and raw.get("next_item_id") >= 1
                else 1,
            ),
            "created_at": str(raw.get("created_at") or ""),
            "updated_at": str(raw.get("updated_at") or ""),
        })

    return cleaned


def create_milestone(
    milestone_id: int,
    title: str,
    end_date: Any,
    section: str = "Other",
    color: str = "Blue",
    emoji: str = "🎯",
    now: str = "",
) -> dict[str, Any]:
    """Create a validated empty milestone record."""
    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValueError("Enter a milestone title.")
    if section not in MILESTONE_SECTIONS:
        raise ValueError("Choose a valid milestone section.")
    if color not in PALETTE:
        raise ValueError("Choose a valid milestone color.")
    if emoji not in MILESTONE_EMOJIS:
        raise ValueError("Choose a valid milestone icon.")

    timestamp = str(now or "")
    return {
        "id": int(milestone_id),
        "title": clean_title,
        "end_date": _normalize_date(end_date),
        "section": section,
        "color": color,
        "emoji": emoji,
        "checklist": [],
        "next_item_id": 1,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def add_checklist_item(milestone: dict[str, Any], text: str) -> dict[str, Any]:
    """Append a new unchecked checklist item with the next unused ID."""
    clean_text = str(text or "").strip()
    if not clean_text:
        raise ValueError("Enter a checklist item.")

    checklist = milestone.setdefault("checklist", [])
    valid_ids = [
        item.get("id") for item in checklist
        if isinstance(item, dict)
        and isinstance(item.get("id"), int)
        and not isinstance(item.get("id"), bool)
        and item.get("id") > 0
    ]
    item_id = max(
        int(milestone.get("next_item_id", 1))
        if isinstance(milestone.get("next_item_id"), int)
        and not isinstance(milestone.get("next_item_id"), bool)
        and milestone.get("next_item_id") > 0
        else 1,
        max(valid_ids, default=0) + 1,
    )
    item = {"id": item_id, "text": clean_text, "done": False}
    checklist.append(item)
    milestone["next_item_id"] = item_id + 1
    return item


def update_checklist_item(
    milestone: dict[str, Any],
    item_id: int,
    text: str,
) -> None:
    """Update one checklist item while preserving its completed status."""
    clean_text = str(text or "").strip()
    if not clean_text:
        raise ValueError("Checklist item cannot be empty.")

    item = next(
        (
            row for row in milestone.get("checklist", [])
            if isinstance(row, dict) and row.get("id") == item_id
        ),
        None,
    )
    if item is None:
        raise KeyError("Checklist item was not found.")
    item["text"] = clean_text


def set_checklist_item_done(
    milestone: dict[str, Any],
    item_id: int,
    done: bool,
) -> None:
    """Cross off or reopen one checklist item."""
    item = next(
        (
            row for row in milestone.get("checklist", [])
            if isinstance(row, dict) and row.get("id") == item_id
        ),
        None,
    )
    if item is None:
        raise KeyError("Checklist item was not found.")
    item["done"] = bool(done)


def delete_checklist_item(milestone: dict[str, Any], item_id: int) -> bool:
    """Delete an item and return whether an item was removed."""
    checklist = milestone.get("checklist", [])
    retained = [
        item for item in checklist
        if not (isinstance(item, dict) and item.get("id") == item_id)
    ]
    removed = len(retained) != len(checklist)
    milestone["checklist"] = retained
    return removed


def update_milestone(
    milestone: dict[str, Any],
    *,
    title: str,
    end_date: Any,
    section: str,
    color: str,
    emoji: str,
) -> None:
    """Validate and update milestone metadata without changing its checklist."""
    updated = create_milestone(
        milestone_id=milestone.get("id", 1),
        title=title,
        end_date=end_date,
        section=section,
        color=color,
        emoji=emoji,
        now=milestone.get("created_at", ""),
    )
    for field in ("title", "end_date", "section", "color", "emoji"):
        milestone[field] = updated[field]
