"""Responsive SVG clocks and hands-on visual labs for Analog Clock Foundations."""

from __future__ import annotations

import html
import streamlit as st

import clock_math


INK = "#23323D"
BLUE = "#2563A6"
AMBER = "#C47C1E"
GRID = "#DDE5E9"
MUTED = "#61727D"


def clock_svg(hour: int, minute: int, *, title: str = "Analog clock") -> str:
    """Render a responsive, labelled clock face with separately identified hands."""
    hour_value = int(hour) % 12 or 12
    minute_value = int(minute) % 60
    cx = cy = 150
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" role="img" '
        f'aria-label="{html.escape(title)} showing {hour_value}:{minute_value:02d}" '
        'style="display:block;width:min(100%,330px);height:auto;margin:auto;background:#FFFFFF;border:1px solid #DDE5E9;border-radius:14px">',
        f'<title>{html.escape(title)} — {hour_value}:{minute_value:02d}</title>',
        '<circle cx="150" cy="150" r="132" fill="#FFFFFF" stroke="#9AAAB2" stroke-width="2.5"/>',
    ]

    for tick in range(60):
        angle = tick * 6
        radians = __import__("math").radians(angle)
        major = tick % 5 == 0
        outer = 124
        inner = 112 if major else 119
        x1 = cx + __import__("math").sin(radians) * inner
        y1 = cy - __import__("math").cos(radians) * inner
        x2 = cx + __import__("math").sin(radians) * outer
        y2 = cy - __import__("math").cos(radians) * outer
        stroke = AMBER if major else GRID
        width = 3.2 if major else 1.4
        parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"/>'
        )

    for number in range(1, 13):
        angle = number * 30
        radians = __import__("math").radians(angle)
        radius = 96
        x = cx + __import__("math").sin(radians) * radius
        y = cy - __import__("math").cos(radians) * radius + 6
        parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" '
            f'font-family="Arial,sans-serif" font-size="20" font-weight="600" fill="{INK}">{number}</text>'
        )

    hx, hy = clock_math.hand_endpoint(clock_math.hour_hand_angle(hour_value, minute_value), 67)
    mx, my = clock_math.hand_endpoint(clock_math.minute_hand_angle(minute_value), 103)
    parts.extend([
        f'<line x1="{cx}" y1="{cy}" x2="{hx:.2f}" y2="{hy:.2f}" stroke="{BLUE}" stroke-width="9" stroke-linecap="round"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{mx:.2f}" y2="{my:.2f}" stroke="{AMBER}" stroke-width="5" stroke-linecap="round"/>',
        f'<circle cx="{cx}" cy="{cy}" r="7" fill="{INK}"/>',
        '</svg>',
    ])
    return "".join(parts)


def _clock_card(hour: int, minute: int, title: str, detail: str) -> None:
    st.markdown(f"**{title}**")
    st.markdown(clock_svg(hour, minute, title=title), unsafe_allow_html=True)
    st.caption(detail)


def _render_clock_lab(key_prefix: str, *, default_hour: int = 7, default_minute: int = 25) -> None:
    st.markdown("**Clock explorer — move the hands and watch both readings change**")
    hour_col, minute_col = st.columns(2)
    with hour_col:
        hour = st.slider(
            "Hour", min_value=1, max_value=12, value=default_hour,
            key=f"{key_prefix}_hour",
        )
    with minute_col:
        minute = st.slider(
            "Minute", min_value=0, max_value=59, value=default_minute,
            key=f"{key_prefix}_minute",
        )
    st.markdown(clock_svg(hour, minute, title="Your selected time"), unsafe_allow_html=True)
    groups, extra = clock_math.minute_count(minute)
    current_hour, next_hour = clock_math.hour_interval(hour, minute)
    st.markdown(
        f"**Digital reading: {hour}:{minute:02d}** · **{clock_math.spoken_time(hour, minute)}**"
    )
    st.write(
        f"Minute hand: {groups} groups of five ({groups} × 5 = {groups * 5}) "
        f"plus {extra} small minute mark(s) = {minute} minutes."
    )
    if minute == 0:
        st.write(f"Hour hand: exactly on {current_hour}; a new hour is beginning.")
    else:
        st.write(
            f"Hour hand: between {current_hour} and {next_hour}; "
            f"it has passed {current_hour} but has not reached {next_hour}."
        )


def render_lesson_visual(lesson: dict, *, key_prefix: str = "clock") -> None:
    """Render the visual explanation associated with one course lesson."""
    visual_key = lesson.get("visual_key")
    st.markdown("#### See the clock, not just the rule")

    if visual_key == "clock_foundation":
        left, right = st.columns(2)
        with left:
            _clock_card(3, 0, "3:00", "The long minute hand is at 12; the short hour hand is at 3.")
        with right:
            _clock_card(3, 30, "3:30", "The long hand has made half a turn; the short hand has moved halfway toward 4.")
        st.info(
            "Blue short hand = hours. Amber long hand = minutes. "
            "The minute hand completes a full circle in 60 minutes."
        )
        _clock_card(4, 0, "4:00", "After the full minute-hand turn, the hour hand reaches 4.")

    elif visual_key == "clock_minute_counting":
        left, right = st.columns(2)
        with left:
            _clock_card(2, 23, "2:23", "Minute count: 4 groups of five = 20, then 3 extra ticks = 23.")
        with right:
            st.markdown("**Count the numbered marks**")
            st.markdown(
                "<div style='padding:12px;border:1px solid #DDE5E9;border-radius:12px;background:#FFFFFF;'>"
                "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:7px;text-align:center;'>"
                + "".join(
                    f"<div style='padding:8px 4px;border-radius:8px;background:#F3F6F8;'><strong>{n}</strong><br><span>{n*5} min</span></div>"
                    for n in range(1, 13)
                )
                + "</div></div>",
                unsafe_allow_html=True,
            )
            st.caption("The small marks between the large numbers each add one minute.")
        _render_clock_lab(f"{key_prefix}_minute_lab", default_hour=2, default_minute=23)

    elif visual_key == "clock_hour_position":
        columns = st.columns(3)
        examples = [(3, 5), (3, 30), (3, 55)]
        captions = [
            "A little past 3",
            "Halfway between 3 and 4",
            "Very close to 4, but still 3:55",
        ]
        for column, (hour, minute), detail in zip(columns, examples, captions):
            with column:
                _clock_card(hour, minute, f"{hour}:{minute:02d}", detail)
        st.warning("Read the hour number the short hand has PASSED — not the number it is nearest to.")
        _render_clock_lab(f"{key_prefix}_hour_lab", default_hour=3, default_minute=55)

    elif visual_key == "clock_reading":
        st.markdown(
            "The long hand gives the minute value. The short hand tells which hour has already started. "
            "Read them in that order, then combine the values."
        )
        _render_clock_lab(f"{key_prefix}_reading_lab", default_hour=9, default_minute=25)

    elif visual_key == "clock_elapsed":
        left, right = st.columns(2)
        with left:
            _clock_card(2, 47, "Start · 2:47", "Move 13 minutes forward to reach 3:00.")
        with right:
            _clock_card(3, 18, "Finish · 3:18", "Then move another 18 minutes to reach 3:18.")
        st.markdown(
            "<div style='padding:12px;border:1px solid #DDE5E9;border-radius:12px;text-align:center;'>"
            "<strong>13 minutes</strong> to 3:00 + <strong>18 minutes</strong> after 3:00 "
            "= <strong>31 minutes elapsed</strong></div>",
            unsafe_allow_html=True,
        )
        _render_clock_lab(f"{key_prefix}_elapsed_lab", default_hour=2, default_minute=47)
    else:
        st.caption("Use the clock explorer in the earlier lessons, then complete this check without the visual prompts.")
