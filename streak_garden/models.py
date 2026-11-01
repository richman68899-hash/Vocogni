"""Typed domain models and JSON-safe state validation for Streak Garden.

Vocogni currently stores learner state in the learner_progress.progress JSONB
record. Streak Garden is an additive, versioned object in that existing
record; v1 does not introduce a second persistence path or new SQL tables.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .enums import GrowthStage, TreeStatus

SCHEMA_VERSION = 1
DEFAULT_TARGET_DAYS = 5
DEFAULT_CYCLE_DAYS = 7
DEFAULT_TREE_CAPACITY = 10


@dataclass(frozen=True)
class Garden:
    id: str
    name: str
    created_on: date | None
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class Forest:
    course_id: str
    name: str
    anchor_date: date
    target_days: int = DEFAULT_TARGET_DAYS
    cycle_days: int = DEFAULT_CYCLE_DAYS
    tree_capacity: int = DEFAULT_TREE_CAPACITY


@dataclass(frozen=True)
class Tree:
    id: str
    forest_id: str
    cycle_start: date
    growth_stage: GrowthStage
    status: TreeStatus
    planted_on: date
    sold_on: date | None = None


@dataclass(frozen=True)
class WalletTransaction:
    id: str
    source_key: str
    amount: int
    reason: str
    created_on: date


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _safe_text(value: Any, fallback: str = "", limit: int = 100) -> str:
    if not isinstance(value, str):
        return fallback
    value = value.strip()
    return value[:limit] if value else fallback


def default_garden_state() -> dict[str, Any]:
    """Return an empty garden state that older learner records can adopt."""
    return {
        "schema_version": SCHEMA_VERSION,
        "id": "academic-garden",
        "name": "Academic Garden",
        "created_on": None,
        "forests": {},
        "trees": [],
        "wallet_transactions": [],
    }


def sanitize_garden_state(value: Any) -> dict[str, Any]:
    """Validate saved garden data while preserving valid achievement history."""
    result = default_garden_state()
    if not isinstance(value, dict):
        return result

    try:
        version = int(value.get("schema_version", SCHEMA_VERSION))
    except (TypeError, ValueError):
        version = SCHEMA_VERSION
    if version != SCHEMA_VERSION:
        return result

    result["id"] = _safe_text(value.get("id"), result["id"], 80)
    result["name"] = _safe_text(value.get("name"), result["name"], 80)
    created_on = _as_date(value.get("created_on"))
    result["created_on"] = created_on.isoformat() if created_on else None

    raw_forests = value.get("forests", {})
    if isinstance(raw_forests, dict):
        for raw_course_id, raw_forest in raw_forests.items():
            course_id = _safe_text(raw_course_id, "", 100)
            if not course_id or not isinstance(raw_forest, dict):
                continue
            anchor = _as_date(raw_forest.get("anchor_date"))
            if anchor is None:
                continue
            try:
                target = int(raw_forest.get("target_days", DEFAULT_TARGET_DAYS))
                capacity = int(raw_forest.get("tree_capacity", DEFAULT_TREE_CAPACITY))
            except (TypeError, ValueError):
                target, capacity = DEFAULT_TARGET_DAYS, DEFAULT_TREE_CAPACITY
            if not 1 <= target <= DEFAULT_CYCLE_DAYS:
                target = DEFAULT_TARGET_DAYS
            if capacity not in (5, 10):
                capacity = DEFAULT_TREE_CAPACITY
            result["forests"][course_id] = {
                "course_id": course_id,
                "name": _safe_text(raw_forest.get("name"), course_id, 100),
                "anchor_date": anchor.isoformat(),
                "target_days": target,
                "cycle_days": DEFAULT_CYCLE_DAYS,
                "tree_capacity": capacity,
            }

    raw_trees = value.get("trees", [])
    seen_tree_ids = set()
    seen_tree_cycles = set()
    if isinstance(raw_trees, list):
        for raw_tree in raw_trees:
            if not isinstance(raw_tree, dict):
                continue
            tree_id = _safe_text(raw_tree.get("id"), "", 180)
            forest_id = _safe_text(raw_tree.get("forest_id"), "", 100)
            cycle_start = _as_date(raw_tree.get("cycle_start"))
            planted_on = _as_date(raw_tree.get("planted_on"))
            try:
                stage = GrowthStage(int(raw_tree.get("growth_stage", 1)))
            except (TypeError, ValueError):
                continue
            status = raw_tree.get("status", TreeStatus.ACTIVE.value)
            if status not in (TreeStatus.ACTIVE.value, TreeStatus.SOLD.value):
                continue
            if (
                not tree_id or tree_id in seen_tree_ids or not forest_id
                or cycle_start is None or planted_on is None
            ):
                continue
            cycle_identity = (forest_id, cycle_start.isoformat())
            if cycle_identity in seen_tree_cycles:
                continue
            sold_on = _as_date(raw_tree.get("sold_on"))
            seen_tree_ids.add(tree_id)
            seen_tree_cycles.add(cycle_identity)
            result["trees"].append({
                "id": tree_id,
                "forest_id": forest_id,
                "cycle_start": cycle_start.isoformat(),
                "growth_stage": int(stage),
                "status": status,
                "planted_on": planted_on.isoformat(),
                "sold_on": sold_on.isoformat() if sold_on else None,
            })

    raw_transactions = value.get("wallet_transactions", [])
    seen_sources = set()
    if isinstance(raw_transactions, list):
        for raw_transaction in raw_transactions:
            if not isinstance(raw_transaction, dict):
                continue
            source_key = _safe_text(raw_transaction.get("source_key"), "", 220)
            transaction_date = _as_date(raw_transaction.get("created_on"))
            reason = _safe_text(raw_transaction.get("reason"), "", 40)
            try:
                amount = int(raw_transaction.get("amount"))
            except (TypeError, ValueError):
                continue
            if (
                not source_key or source_key in seen_sources
                or transaction_date is None or not reason or amount == 0
            ):
                continue
            seen_sources.add(source_key)
            result["wallet_transactions"].append({
                "id": _safe_text(raw_transaction.get("id"), source_key, 220),
                "source_key": source_key,
                "amount": amount,
                "reason": reason,
                "created_on": transaction_date.isoformat(),
            })

    return result
