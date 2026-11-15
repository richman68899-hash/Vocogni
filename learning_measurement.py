"""Consistent descriptive pre/post lesson checkpoint calculations.

Transfer checks are intentionally independent evidence. They must not enter
ordinary practice accuracy or its denominator.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any


def _normalise_baseline_percent(value: Any) -> int:
    """Return a finite whole-number percentage constrained to the 0–100 scale."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    if isinstance(value, int):
        return min(100, max(0, value))
    if not math.isfinite(value):
        return 0
    return min(100, max(0, int(value)))


def build_post_lesson_checkpoint(
    baseline: Any,
    results: Any,
    *,
    pathway: str = "unknown",
    completed_at: str | None = None,
) -> dict[str, Any] | None:
    """Build a descriptive checkpoint from ordinary practice answers only.

    Returns None when there is no usable baseline or no ordinary practice
    result. Independent transfer checks are deliberately excluded from both
    numerator and denominator.
    """
    if not isinstance(baseline, dict) or not isinstance(results, list):
        return None

    ordinary = [
        result for result in results
        if isinstance(result, dict)
        and result.get("evidence_type") != "independent_transfer"
        and isinstance(result.get("correct"), bool)
    ]
    if not ordinary:
        return None

    baseline_percent = _normalise_baseline_percent(baseline.get("percent", 0))

    post_correct = sum(1 for result in ordinary if result["correct"])
    post_total = len(ordinary)
    post_percent = round(post_correct / post_total * 100)

    return {
        "baseline_score": baseline.get("score", 0),
        "baseline_total": baseline.get("total", 5),
        "baseline_percent": baseline_percent,
        "post_correct": post_correct,
        "post_total": post_total,
        "post_practice_percent": post_percent,
        "percentage_point_difference": post_percent - baseline_percent,
        "pathway": pathway if isinstance(pathway, str) else "unknown",
        "completed_at": completed_at or datetime.now(timezone.utc).isoformat(),
    }


__all__ = ["build_post_lesson_checkpoint"]
