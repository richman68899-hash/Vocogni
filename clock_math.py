"""Pure time and hand-position logic for the analog-clock course."""

from __future__ import annotations


def minute_hand_angle(minute: int) -> float:
    """Clockwise degrees from 12 o'clock for the minute hand."""
    return (int(minute) % 60) * 6.0


def hour_hand_angle(hour: int, minute: int = 0) -> float:
    """Clockwise degrees from 12 o'clock; the hour hand moves continuously."""
    return (((int(hour) % 12) * 60) + (int(minute) % 60)) * 0.5


def hand_endpoint(angle_degrees: float, length: float, *, centre: float = 150.0) -> tuple[float, float]:
    """Return an SVG endpoint for a clockwise angle measured from 12 o'clock."""
    import math

    radians = math.radians(float(angle_degrees))
    return (
        centre + math.sin(radians) * float(length),
        centre - math.cos(radians) * float(length),
    )


def minute_count(minute: int) -> tuple[int, int]:
    """Return (groups of five, extra minute ticks) for a minute value."""
    value = int(minute) % 60
    return divmod(value, 5)


def hour_interval(hour: int, minute: int) -> tuple[int, int]:
    """Return the hour just passed and the next hour on a 12-hour clock."""
    current = int(hour) % 12 or 12
    following = current % 12 + 1
    return current, following


def spoken_time(hour: int, minute: int) -> str:
    """Return common classroom language for an analog-clock time."""
    h = int(hour) % 12 or 12
    m = int(minute) % 60
    next_hour = h % 12 + 1
    if m == 0:
        return f"{h} o'clock"
    if m == 15:
        return f"quarter past {h}"
    if m == 30:
        return f"half past {h}"
    if m == 45:
        return f"quarter to {next_hour}"
    if m < 30:
        unit = "minute" if m == 1 else "minutes"
        return f"{m} {unit} past {h}"
    remaining = 60 - m
    unit = "minute" if remaining == 1 else "minutes"
    return f"{remaining} {unit} to {next_hour}"


def elapsed_minutes(start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> int:
    """Elapsed minutes between two times on a 12-hour dial (0–719 minutes)."""
    start = ((int(start_hour) % 12) * 60) + (int(start_minute) % 60)
    end = ((int(end_hour) % 12) * 60) + (int(end_minute) % 60)
    return (end - start) % 720
