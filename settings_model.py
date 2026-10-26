"""Pure settings defaults and helpers, independent of Streamlit."""
from __future__ import annotations

from typing import Any
import re


DEFAULT_SETTINGS: dict[str, Any] = {
    "appearance": "Light",
    "text_size": "Medium",
    "animations": True,
    "sound": True,
    "feedback_timing": "Immediate",
    "difficulty": "Adaptive",
    "reduced_motion": False,
    "larger_text": False,
    "high_readability": False,
    # Decorative preferences are saved in the same backward-compatible bundle.
    "font_family": "Inter",
    "background_tone": "Neutral",
    "corner_style": "Standard",
    "use_custom_accent": False,
    "custom_accent_color": "#176B5B",
}

SETTING_WIDGET_KEYS = {
    "appearance": "settings_appearance",
    "text_size": "settings_text_size",
    "feedback_timing": "settings_feedback_timing",
    "difficulty": "settings_difficulty",
    "animations": "settings_animations",
    "sound": "settings_sound",
    "larger_text": "settings_larger_text",
    "high_readability": "settings_high_readability",
    "font_family": "settings_font_family",
    "background_tone": "settings_background_tone",
    "corner_style": "settings_corner_style",
    "use_custom_accent": "settings_use_custom_accent",
    "custom_accent_color": "settings_custom_accent_color",
}

SETTING_OPTIONS = {
    "appearance": ["Light", "Dark"],
    "text_size": ["Small", "Medium", "Large"],
    "feedback_timing": ["Immediate", "After submission"],
    "difficulty": ["Adaptive", "Easy", "Hard"],
    "font_family": ["Inter", "Manrope", "Atkinson Hyperlegible", "Source Serif 4"],
    "background_tone": ["Neutral", "Warm", "Cool"],
    "corner_style": ["Standard", "Rounded", "Square"],
}

PRESETS: dict[str, dict[str, Any]] = {
    "Focused study": {
        "animations": False,
        "sound": False,
        "reduced_motion": True,
        "feedback_timing": "After submission",
    },
    "Reading comfort": {
        "text_size": "Large",
        "larger_text": True,
        "high_readability": True,
        "reduced_motion": True,
        "animations": False,
    },
    "Gentle practice": {
        "difficulty": "Easy",
        "feedback_timing": "Immediate",
        "sound": False,
    },
}


def safe_value(key: str, value: Any) -> Any:
    """Return a supported setting value without breaking older learner data."""
    # Before the hint-assistance labels, Medium was an exposed preference but
    # had no distinct behavior. Map it to the existing on-request behavior.
    if key == "difficulty" and value == "Medium":
        return "Adaptive"
    if key == "custom_accent_color":
        # Keep arbitrary persisted values from becoming CSS or HTML injection.
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value.strip()):
            return value.strip().upper()
        return DEFAULT_SETTINGS[key]
    if key in SETTING_OPTIONS:
        return value if value in SETTING_OPTIONS[key] else DEFAULT_SETTINGS[key]
    if key not in DEFAULT_SETTINGS:
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "yes", "1", "on"}:
            return True
        if normalized in {"false", "no", "0", "off", ""}:
            return False
    return bool(value)


def settings_changed(settings: dict[str, Any], new_values: dict[str, Any]) -> bool:
    """Return True only when a durable preference changes."""
    return any(settings.get(key) != value for key, value in new_values.items())


def current_summary(settings: dict[str, Any]) -> str:
    """Create a compact summary of the selected settings."""
    theme = settings.get("appearance", "Light")
    text = settings.get("text_size", "Medium")
    feedback = settings.get("feedback_timing", "Immediate")
    motion = (
        "Motion reduced"
        if settings.get("reduced_motion") or not settings.get("animations", True)
        else "Motion enabled"
    )
    sound = "Sound on" if settings.get("sound", True) else "Sound off"
    font = settings.get("font_family", "Inter")
    tone = settings.get("background_tone", "Neutral")
    corners = settings.get("corner_style", "Standard")
    accent = "custom accent" if settings.get("use_custom_accent", False) else "theme accent"
    return (
        f"{theme} theme  ·  {font} font  ·  {text} text  ·  "
        f"{tone.lower()} background  ·  {corners.lower()} corners  ·  "
        f"{feedback.lower()} feedback  ·  {motion}  ·  {sound}  ·  {accent}"
    )
