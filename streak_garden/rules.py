"""Pure, framework-independent progression rules for Streak Garden."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

from .enums import GrowthStage


def as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise TypeError("Expected a date, datetime, or ISO date string.")


def calculate_streak_summary(active_dates: Iterable[date], today: date) -> dict:
    """A streak remains current through today when its last day was yesterday."""
    today = as_date(today)
    dates = {as_date(item) for item in active_dates if item is not None}
    ordered = sorted(dates)

    longest = run = 0
    previous = None
    for active_day in ordered:
        run = run + 1 if previous and active_day == previous + timedelta(days=1) else 1
        longest = max(longest, run)
        previous = active_day

    anchor = today if today in dates else today - timedelta(days=1)
    current = 0
    if anchor in dates:
        cursor = anchor
        while cursor in dates:
            current += 1
            cursor -= timedelta(days=1)

    return {
        "current_streak": current,
        "longest_streak": longest,
        "today_complete": today in dates,
        "last_active_day": ordered[-1] if ordered else None,
    }


def cycle_window(anchor_date: date, today: date, cycle_days: int = 7) -> tuple[date, date]:
    """Return the fixed cycle containing today for a forest."""
    anchor_date = as_date(anchor_date)
    today = as_date(today)
    if cycle_days < 1:
        raise ValueError("cycle_days must be positive.")
    if today < anchor_date:
        return anchor_date, anchor_date + timedelta(days=cycle_days - 1)
    index = (today - anchor_date).days // cycle_days
    start = anchor_date + timedelta(days=index * cycle_days)
    return start, start + timedelta(days=cycle_days - 1)


def calculate_cycle_progress(
    active_dates: Iterable[date],
    anchor_date: date,
    today: date,
    target_days: int = 5,
    cycle_days: int = 7,
) -> dict:
    """Calculate current-cycle progress using unique local calendar days."""
    if target_days < 1 or target_days > cycle_days:
        raise ValueError("target_days must be between 1 and cycle_days.")
    today = as_date(today)
    start, end = cycle_window(anchor_date, today, cycle_days)
    if today < start:
        eligible_dates = set()
    else:
        eligible_dates = {
            as_date(item) for item in active_dates
            if start <= as_date(item) <= min(end, today)
        }
    qualifying_days = len(eligible_dates)
    return {
        "cycle_start": start,
        "cycle_end": end,
        "qualifying_days": qualifying_days,
        "target_days": target_days,
        "percentage": min(100, round(qualifying_days / target_days * 100)),
        "completed": qualifying_days >= target_days,
    }


def growth_stage_for_days(qualifying_days: int, target_days: int = 5) -> GrowthStage | None:
    """Target days plant a seedling; one and two extra days grow it further."""
    if qualifying_days < target_days:
        return None
    extra_days = qualifying_days - target_days
    if extra_days == 0:
        return GrowthStage.SEEDLING
    if extra_days == 1:
        return GrowthStage.SAPLING
    return GrowthStage.MATURE


def dew_balance(transactions: Iterable[dict]) -> int:
    """Calculate wallet balance from the append-only transaction ledger."""
    total = 0
    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue
        amount = transaction.get("amount")
        if isinstance(amount, int) and not isinstance(amount, bool):
            total += amount
    return total


def tree_sale_value(growth_stage: int) -> int:
    """Prototype resale value for a tree's current growth stage."""
    values = {
        GrowthStage.SEEDLING: 5,
        GrowthStage.SAPLING: 10,
        GrowthStage.MATURE: 15,
    }
    return values[GrowthStage(int(growth_stage))]
