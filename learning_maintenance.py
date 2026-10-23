"""Lightweight, evidence-aligned learning maintenance for Vocogni.

This module is framework-free. It derives streaks and review scheduling from
existing saved practice attempts, diagnostics, and completed screen checkpoints.
It does not award points, coins, badges, or count app opens as learning.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

import data

WEEKLY_TARGET_OPTIONS = (2, 3, 4, 5)
DEFAULT_WEEKLY_TARGET = 3
REVIEW_INTERVALS_DAYS = (1, 3, 7)


def timezone_from_profile(value):
    """Parse profile values such as 'UTC+7' and 'UTC+5:30'; safely default to UTC."""
    if not isinstance(value, str):
        return timezone.utc
    match = re.fullmatch(r"\s*UTC([+-])(\d{1,2})(?::(\d{2}))?\s*", value)
    if not match:
        return timezone.utc
    sign = 1 if match.group(1) == "+" else -1
    hours = int(match.group(2))
    minutes = int(match.group(3) or 0)
    if hours > 14 or minutes > 59 or (hours == 14 and minutes):
        return timezone.utc
    offset = timedelta(minutes=sign * (hours * 60 + minutes))
    return timezone(offset, name=value.strip())


def _parse_timestamp(value):
    """Parse an ISO timestamp; legacy naive timestamps are interpreted as UTC."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _local_date(timestamp, tz):
    parsed = _parse_timestamp(timestamp)
    return parsed.astimezone(tz).date() if parsed else None


def _valid_results(record):
    results = record.get("results", []) if isinstance(record, dict) else []
    return results if isinstance(results, list) and results else []


def _iter_course_progress(progress):
    if not isinstance(progress, dict):
        return
    for course_id, course_progress in progress.items():
        if data.get_course(course_id) and isinstance(course_progress, dict):
            yield course_id, course_progress


def _attempt_percent(attempt):
    """Calculate a descriptive attempt percentage from its stored item results."""
    results = _valid_results(attempt)
    if not results:
        return None
    ratios = []
    for result in results:
        if not isinstance(result, dict):
            continue
        ratio = None
        for score_field in ("score", "marks_awarded"):
            try:
                maximum = float(result.get("max_marks"))
                earned = float(result.get(score_field))
                if maximum > 0:
                    ratio = min(1.0, max(0.0, earned / maximum))
                    break
            except (TypeError, ValueError):
                continue
        if ratio is None:
            ratio = 1.0 if bool(result.get("correct")) else 0.0
        ratios.append(ratio)
    return round(sum(ratios) / len(ratios) * 100) if ratios else None


def _completed_attempt_events(course_progress, tz):
    """Yield (lesson_id, local_date, percent) for timestamped completed practice sets."""
    attempts_by_lesson = course_progress.get("practice_attempts", {})
    if not isinstance(attempts_by_lesson, dict):
        attempts_by_lesson = {}
    found_by_lesson = {}
    for lesson_id, attempts in attempts_by_lesson.items():
        if not isinstance(attempts, list):
            continue
        rows = []
        for attempt in attempts:
            if not isinstance(attempt, dict) or not _valid_results(attempt):
                continue
            completed_at = _parse_timestamp(attempt.get("completed_at"))
            if completed_at is None:
                continue
            rows.append({
                "lesson_id": str(lesson_id),
                "completed_at": completed_at,
                "local_date": completed_at.astimezone(tz).date(),
                "percent": _attempt_percent(attempt),
            })
        if rows:
            found_by_lesson[str(lesson_id)] = rows

    # Compatibility fallback: some completed screen checkpoints may have a
    # complete result payload but no finalized practice_attempts entry.
    checkpoints = course_progress.get("lesson_screen_progress", {})
    if isinstance(checkpoints, dict):
        for lesson_id, checkpoint in checkpoints.items():
            lesson_id = str(lesson_id)
            if lesson_id in found_by_lesson:
                continue
            if not isinstance(checkpoint, dict):
                continue
            if not (
                checkpoint.get("completed")
                and checkpoint.get("screen_3_submitted")
                and _valid_results(checkpoint)
            ):
                continue
            completed_at = _parse_timestamp(checkpoint.get("updated_at"))
            if completed_at is None:
                continue
            found_by_lesson[lesson_id] = [{
                "lesson_id": lesson_id,
                "completed_at": completed_at,
                "local_date": completed_at.astimezone(tz).date(),
                "percent": _attempt_percent({"results": checkpoint.get("results", [])}),
            }]
    return found_by_lesson


def activity_dates(progress, timezone_label="Prefer not to say"):
    """Return unique local dates with meaningful completed learning activity.

    A day counts when a learner submits an answer that is saved with feedback,
    completes a practice set, or submits a diagnostic. Opening the app or merely
    viewing content does not count.
    """
    tz = timezone_from_profile(timezone_label)
    active_dates = set()
    for _course_id, course_progress in _iter_course_progress(progress):
        attempts = _completed_attempt_events(course_progress, tz)
        for lesson_attempts in attempts.values():
            active_dates.update(item["local_date"] for item in lesson_attempts)

        # A saved answer with feedback is meaningful activity even if the
        # learner leaves before finishing the entire practice set. Keep this
        # separate from review scheduling: incomplete attempts count as
        # activity, but do not create a spaced-review due date.
        checkpoints = course_progress.get("lesson_screen_progress", {})
        if isinstance(checkpoints, dict):
            for checkpoint in checkpoints.values():
                if not isinstance(checkpoint, dict):
                    continue
                if not checkpoint.get("screen_3_submitted") or not _valid_results(checkpoint):
                    continue
                active_day = _local_date(checkpoint.get("updated_at"), tz)
                if active_day is not None:
                    active_dates.add(active_day)

        diagnostics = course_progress.get("diagnostics", {})
        if isinstance(diagnostics, dict):
            for record in diagnostics.values():
                if isinstance(record, dict) and _parse_timestamp(record.get("completed_at")):
                    active_dates.add(_local_date(record.get("completed_at"), tz))
    active_dates.discard(None)
    return active_dates


def _longest_streak(sorted_dates):
    longest = run = 0
    previous = None
    for active_day in sorted_dates:
        if previous is not None and active_day == previous + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        previous = active_day
    return longest


def _current_streak(active_dates, today):
    if today in active_dates:
        anchor = today
    elif today - timedelta(days=1) in active_dates:
        anchor = today - timedelta(days=1)
    else:
        return 0
    run = 0
    cursor = anchor
    while cursor in active_dates:
        run += 1
        cursor -= timedelta(days=1)
    return run


def _review_history(progress, tz):
    """Build current lesson review schedules from completed, timestamped attempts."""
    histories = []
    for course_id, course_progress in _iter_course_progress(progress):
        course = data.get_course(course_id)
        lesson_attempts = _completed_attempt_events(course_progress, tz)
        if not lesson_attempts:
            continue
        for lesson_id, attempts in lesson_attempts.items():
            lesson, _ = data.get_lesson(course_id, lesson_id)
            if not lesson:
                continue
            attempts = sorted(attempts, key=lambda row: row["completed_at"])
            session_days = sorted({row["local_date"] for row in attempts})
            latest = attempts[-1]
            latest_percent = latest["percent"]

            # Adaptive, deliberately simple heuristic: bring weaker work back
            # sooner; otherwise increase the spacing as the learner revisits it
            # on distinct days. These intervals are a product heuristic, not a
            # claim that 1/3/7 days is universally optimal.
            if latest_percent is not None and latest_percent < 60:
                interval_days = 1
            elif latest_percent is not None and latest_percent < 80:
                interval_days = 2
            else:
                interval_days = REVIEW_INTERVALS_DAYS[min(len(session_days) - 1, 2)]

            due_date = latest["local_date"] + timedelta(days=interval_days)
            histories.append({
                "course_id": course_id,
                "course_title": course.get("title", course.get("topic_label", course_id)),
                "lesson_id": lesson_id,
                "lesson_title": lesson.get("title", lesson_id),
                "last_practised": latest["local_date"],
                "due_date": due_date,
                "days_since_practice": len(session_days),
                "attempt_count": len(attempts),
                "latest_percent": latest_percent,
                "interval_days": interval_days,
            })
    return histories


def build_maintenance_summary(
    progress,
    timezone_label="Prefer not to say",
    weekly_target=DEFAULT_WEEKLY_TARGET,
    today=None,
    review_limit=3,
):
    """Return streak, flexible weekly-goal, and due-review data for the Progress UI."""
    tz = timezone_from_profile(timezone_label)
    if today is None:
        today = datetime.now(tz).date()
    elif isinstance(today, datetime):
        today = today.date()
    if not isinstance(today, date):
        raise TypeError("today must be a date or datetime")

    try:
        weekly_target = int(weekly_target)
    except (TypeError, ValueError):
        weekly_target = DEFAULT_WEEKLY_TARGET
    if weekly_target not in WEEKLY_TARGET_OPTIONS:
        weekly_target = DEFAULT_WEEKLY_TARGET

    active_dates = activity_dates(progress, timezone_label)
    sorted_dates = sorted(active_dates)
    week_start = today - timedelta(days=today.weekday())
    active_this_week = sorted(
        day for day in active_dates if week_start <= day <= today
    )
    week_day_cards = [
        {
            "label": (week_start + timedelta(days=index)).strftime("%a"),
            "date": week_start + timedelta(days=index),
            "active": (week_start + timedelta(days=index)) in active_dates,
            "future": (week_start + timedelta(days=index)) > today,
        }
        for index in range(7)
    ]

    due_reviews = []
    upcoming_reviews = []
    for review in _review_history(progress, tz):
        enriched = dict(review)
        enriched["days_overdue"] = max(0, (today - review["due_date"]).days)
        if review["due_date"] <= today:
            due_reviews.append(enriched)
        else:
            upcoming_reviews.append(enriched)
    due_reviews.sort(
        key=lambda row: (
            row["due_date"],
            row["latest_percent"] if row["latest_percent"] is not None else 101,
            row["course_title"].casefold(),
            row["lesson_title"].casefold(),
        )
    )
    upcoming_reviews.sort(
        key=lambda row: (row["due_date"], row["course_title"].casefold(), row["lesson_title"].casefold())
    )

    last_active_day = sorted_dates[-1] if sorted_dates else None
    return {
        "today": today,
        "active_dates": sorted_dates,
        "today_complete": today in active_dates,
        "current_streak": _current_streak(active_dates, today),
        "longest_streak": _longest_streak(sorted_dates),
        "last_active_day": last_active_day,
        "active_days_this_week": len(active_this_week),
        "weekly_target": weekly_target,
        "week_goal_met": len(active_this_week) >= weekly_target,
        "week_day_cards": week_day_cards,
        "total_due_reviews": len(due_reviews),
        "due_reviews": due_reviews[:max(0, review_limit)],
        "upcoming_reviews": upcoming_reviews[:max(0, review_limit)],
        "review_schedule_note": (
            "Review dates use a simple adaptive spacing rule. Weaker recent work is "
            "scheduled sooner; successful practice is spaced farther apart. The exact "
            "intervals are a practical starting heuristic, not a validated optimal schedule."
        ),
        "activity_definition": (
            "A learning day requires a saved answer with feedback, a completed practice "
            "set, or a completed diagnostic. Opening the app alone does not count."
        ),
    }
