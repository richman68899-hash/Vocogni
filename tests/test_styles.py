"""Regression tests for Vocogni's visual theme and learner display settings."""

import styles


def test_light_theme_uses_consistent_brand_tokens():
    css = styles.build_css({"appearance": "Light"})
    assert "--vc-bg: #F7F8F5;" in css
    assert "--vc-accent: #176B5B;" in css
    assert "--vc-nav-active-bg: #E7F1EB;" in css
    assert "--vc-nav-active-text: #15594B;" in css
    assert "$" not in css


def test_dark_theme_uses_readable_dark_tokens():
    css = styles.build_css({"appearance": "Dark"})
    assert "--vc-bg: #101A17;" in css
    assert "--vc-surface: #17231E;" in css
    assert "--vc-text: #F0F4F0;" in css
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
    assert "transition: none !important;" in css
    assert "scroll-behavior: auto;" in css


def test_icon_text_and_empty_state_alignment_rules_are_present():
    css = styles.build_css({"appearance": "Light"})
    assert ".vc-icon-text" in css
    assert "align-items: center" in css
    assert ".vc-status__icon" in css
    assert ".vc-empty-state" in css
    assert ".vc-login-hero" in css

def test_dark_theme_overrides_native_widget_surfaces_and_text():
    css = styles.build_css({"appearance": "Dark"})
    assert "--background-color: var(--vc-bg);" in css
    assert "--secondary-background-color: var(--vc-surface);" in css
    assert "color-scheme: dark;" in css
    assert "[data-testid=\"stWidgetLabel\"] p" in css
    assert "[data-baseweb=\"select\"] span" in css
    assert "[role=\"listbox\"] [role=\"option\"]:hover" in css
    assert "input::placeholder" in css
    assert "[data-testid=\"stAlert\"] p" in css
    assert "$" not in css


def test_light_theme_keeps_native_controls_theme_aware():
    css = styles.build_css({"appearance": "Light"})
    assert "color-scheme: light;" in css
    assert "--text-color: var(--vc-text);" in css
    assert "background-color: var(--vc-surface) !important;" in css
    assert "$" not in css

