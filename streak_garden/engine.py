"""Deterministic Streak Garden state transitions; no UI or database imports."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from typing import Iterable, Mapping

from .enums import GrowthStage, TreeStatus, WalletReason
from .models import (
    DEFAULT_CYCLE_DAYS,
    DEFAULT_TARGET_DAYS,
    DEFAULT_TREE_CAPACITY,
    default_garden_state,
    sanitize_garden_state,
)
from .rules import (
    calculate_cycle_progress,
    calculate_streak_summary,
    dew_balance,
    growth_stage_for_days,
    tree_sale_value,
)

DAILY_WATER_DEW = 5
TREE_PLANTED_DEW = 25
TREE_STAGE_REWARDS = {
    GrowthStage.SAPLING: 10,
    GrowthStage.MATURE: 15,
}


def initialize_garden_state(
    garden_state: dict | None,
    course_names: Mapping[str, str],
    today: date,
) -> dict:
    """Create the free Academic Garden and one forest per available course."""
    result = sanitize_garden_state(garden_state or default_garden_state())
    if not result.get("created_on"):
        result["created_on"] = today.isoformat()

    for course_id, course_name in course_names.items():
        course_id = str(course_id).strip()
        if not course_id or course_id in result["forests"]:
            continue
        result["forests"][course_id] = {
            "course_id": course_id,
            "name": str(course_name).strip()[:100] or course_id,
            "anchor_date": today.isoformat(),
            "target_days": DEFAULT_TARGET_DAYS,
            "cycle_days": DEFAULT_CYCLE_DAYS,
            "tree_capacity": DEFAULT_TREE_CAPACITY,
        }
    return result


def _transaction_exists(garden_state: dict, source_key: str) -> bool:
    return any(
        item.get("source_key") == source_key
        for item in garden_state.get("wallet_transactions", [])
        if isinstance(item, dict)
    )


def _award(
    garden_state: dict,
    source_key: str,
    amount: int,
    reason: WalletReason,
    created_on: date,
) -> None:
    if amount <= 0 or _transaction_exists(garden_state, source_key):
        return
    garden_state["wallet_transactions"].append({
        "id": source_key,
        "source_key": source_key,
        "amount": int(amount),
        "reason": reason.value,
        "created_on": created_on.isoformat(),
    })


def synchronize_garden(
    garden_state: dict | None,
    course_names: Mapping[str, str],
    active_dates_by_course: Mapping[str, Iterable[date]],
    all_active_dates: Iterable[date],
    today: date,
) -> tuple[dict, bool]:
    """Apply eligible water rewards, trees, growth, and Dew exactly once."""
    original = sanitize_garden_state(garden_state or default_garden_state())
    result = initialize_garden_state(original, course_names, today)
    before = deepcopy(result)
    created_on = date.fromisoformat(result["created_on"])

    # One water reward per local calendar day across all courses.
    for active_day in sorted(set(all_active_dates)):
        if created_on <= active_day <= today:
            _award(
                result,
                f"water:{active_day.isoformat()}",
                DAILY_WATER_DEW,
                WalletReason.DAILY_WATER,
                active_day,
            )

    for course_id, forest in result["forests"].items():
        anchor = date.fromisoformat(forest["anchor_date"])
        if today < anchor:
            continue
        target_days = int(forest["target_days"])
        cycle_days = int(forest["cycle_days"])
        course_days = set(active_dates_by_course.get(course_id, []))
        last_cycle_index = (today - anchor).days // cycle_days

        for cycle_index in range(last_cycle_index + 1):
            cycle_start = anchor + timedelta(days=cycle_index * cycle_days)
            cycle_end = cycle_start + timedelta(days=cycle_days - 1)
            observed_end = min(cycle_end, today)
            qualifying_days = len({
                active_day for active_day in course_days
                if cycle_start <= active_day <= observed_end
            })
            stage = growth_stage_for_days(qualifying_days, target_days)
            if stage is None:
                continue

            cycle_key = f"{course_id}:{cycle_start.isoformat()}"
            tree = next(
                (item for item in result["trees"] if item.get("id") == cycle_key),
                None,
            )
            if tree is not None:
                if tree["status"] != TreeStatus.ACTIVE.value:
                    continue
                old_stage = GrowthStage(int(tree["growth_stage"]))
                if stage > old_stage:
                    tree["growth_stage"] = int(stage)
                    for next_stage in GrowthStage:
                        if old_stage < next_stage <= stage and next_stage in TREE_STAGE_REWARDS:
                            _award(
                                result,
                                f"tree:{cycle_key}:{next_stage.name.lower()}",
                                TREE_STAGE_REWARDS[next_stage],
                                WalletReason.TREE_GROWTH,
                                today,
                            )
                continue

            active_count = sum(
                1 for item in result["trees"]
                if item.get("forest_id") == course_id
                and item.get("status") == TreeStatus.ACTIVE.value
            )
            if active_count >= int(forest["tree_capacity"]):
                # Leave this completed cycle pending. A later tree sale frees a slot.
                continue

            result["trees"].append({
                "id": cycle_key,
                "forest_id": course_id,
                "cycle_start": cycle_start.isoformat(),
                "growth_stage": int(stage),
                "status": TreeStatus.ACTIVE.value,
                "planted_on": today.isoformat(),
                "sold_on": None,
            })
            _award(
                result,
                f"tree:{cycle_key}:planted",
                TREE_PLANTED_DEW,
                WalletReason.TREE_PLANTED,
                today,
            )
            for next_stage in GrowthStage:
                if next_stage <= stage and next_stage in TREE_STAGE_REWARDS:
                    _award(
                        result,
                        f"tree:{cycle_key}:{next_stage.name.lower()}",
                        TREE_STAGE_REWARDS[next_stage],
                        WalletReason.TREE_GROWTH,
                        today,
                    )

    return result, result != before or result != original


def garden_summary(
    garden_state: dict,
    active_dates_by_course: Mapping[str, Iterable[date]],
    all_active_dates: Iterable[date],
    today: date,
) -> dict:
    """Build display-ready streak, wallet, and forest summaries."""
    garden_data = sanitize_garden_state(garden_state)
    streak = calculate_streak_summary(all_active_dates, today)
    forests = []
    for course_id, forest in garden_data["forests"].items():
        progress = calculate_cycle_progress(
            active_dates_by_course.get(course_id, []),
            forest["anchor_date"],
            today,
            target_days=int(forest["target_days"]),
            cycle_days=int(forest["cycle_days"]),
        )
        trees = [
            item for item in garden_data["trees"]
            if item.get("forest_id") == course_id
        ]
        active_trees = [item for item in trees if item["status"] == TreeStatus.ACTIVE.value]
        sold_trees = [item for item in trees if item["status"] == TreeStatus.SOLD.value]
        forests.append({
            **forest,
            **progress,
            "active_trees": active_trees,
            "sold_trees": sold_trees,
            "active_tree_count": len(active_trees),
            "historical_tree_count": len(trees),
            "is_full": len(active_trees) >= int(forest["tree_capacity"]),
            "current_cycle_tree_exists": any(
                item["cycle_start"] == progress["cycle_start"].isoformat()
                for item in trees
            ),
        })
    return {
        "current_streak": streak["current_streak"],
        "longest_streak": streak["longest_streak"],
        "today_complete": streak["today_complete"],
        "dew_balance": dew_balance(garden_data["wallet_transactions"]),
        "forests": forests,
    }


def sell_tree(garden_state: dict, tree_id: str, today: date) -> tuple[dict, int]:
    """Sell one active tree, retain its milestone record, and free its slot."""
    result = sanitize_garden_state(garden_state)
    tree = next((item for item in result["trees"] if item.get("id") == tree_id), None)
    if tree is None:
        raise ValueError("Tree not found.")
    if tree["status"] != TreeStatus.ACTIVE.value:
        raise ValueError("This tree has already been sold.")

    value = tree_sale_value(tree["growth_stage"])
    tree["status"] = TreeStatus.SOLD.value
    tree["sold_on"] = today.isoformat()
    _award(result, f"sale:{tree_id}", value, WalletReason.TREE_SALE, today)
    return result, value
