"""Regression tests for Vocogni's visual theme and learner display settings."""

import styles


def test_light_theme_uses_consistent_brand_tokens():
    css = styles.build_css({"appearance": "Light"})
    assert "--vc-bg: #F7F8F6;" in css
    assert "--vc-accent: #17675F;" in css
    assert "--vc-nav-active-bg: #E6F1EC;" in css
    assert "--vc-nav-active-text: #155A52;" in css
    assert "$" not in css


def test_dark_theme_uses_readable_dark_tokens():
    css = styles.build_css({"appearance": "Dark"})
    assert "--vc-bg: #111916;" in css
    assert "--vc-surface: #18221E;" in css
    assert "--vc-text: #EDF3EF;" in css
    assert "--vc-nav-active-bg: #20372F;" in css
    assert "$" not in css


def test_display_preferences_still_control_type_and_motion():
    css = styles.build_css({
        "appearance": "Light",
        "text_size": "Large",
        "larger_text": True,
        "high_readability": True,
        "animations": False,
    })
    assert "font-size: 19px;" in css
    assert "line-height: 1.82;" in css
    assert "transition: none;" in css
    assert "scroll-behavior: auto;" in css
