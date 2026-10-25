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


def _relative_luminance(hex_color: str) -> float:
    """Calculate WCAG relative luminance for a six-digit hex colour."""
    channels = [
        int(hex_color[index:index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        value / 12.92 if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    luminances = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (luminances[0] + 0.05) / (luminances[1] + 0.05)


def _theme_color(css: str, token: str) -> str:
    import re

    match = re.search(rf"--vc-{token}: (#[0-9A-Fa-f]{{6}});", css)
    assert match, f"Missing colour token: {token}"
    return match.group(1)


def test_runtime_theme_overrides_streamlit_light_component_tokens():
    css = styles.build_css({"appearance": "Dark"})

    # config.toml deliberately remains the default light theme. Runtime
    # appearance must therefore override the component tokens as well.
    assert "color-scheme: dark !important;" in css
    assert "--background-color: var(--vc-bg) !important;" in css
    assert "--secondary-background-color: var(--vc-surface) !important;" in css
    assert "--text-color: var(--vc-text) !important;" in css
    assert "--border-color: var(--vc-border) !important;" in css


def test_dark_mode_covers_inputs_placeholders_and_portal_menus():
    css = styles.build_css({"appearance": "Dark"})

    assert "input::placeholder" in css
    assert "textarea::placeholder" in css
    assert '[data-baseweb="popover"]' in css
    assert '[role="listbox"] [role="option"]' in css
    assert '[data-baseweb="calendar"]' in css
    assert '[data-testid="stAlert"] p' in css
    assert '[data-testid="stMetric"] [data-testid="stMetricValue"]' in css


def test_dark_theme_text_and_interactive_colours_meet_wcag_aa_contrast():
    css = styles.build_css({"appearance": "Dark"})
    backgrounds = [
        _theme_color(css, "bg"),
        _theme_color(css, "surface"),
        _theme_color(css, "surface_alt"),
    ]
    text_colours = [
        _theme_color(css, "text"),
        _theme_color(css, "subtext"),
    ]

    # WCAG AA requires at least 4.5:1 contrast for normal-sized text.
    for foreground in text_colours:
        for background in backgrounds:
            assert _contrast_ratio(foreground, background) >= 4.5, (
                f"Insufficient contrast: {foreground} on {background}"
            )

    assert _contrast_ratio(
        _theme_color(css, "accent"), _theme_color(css, "surface")
    ) >= 4.5
    assert _contrast_ratio(
        _theme_color(css, "nav_active_text"), _theme_color(css, "nav_active_bg")
    ) >= 4.5
    assert _contrast_ratio(
        _theme_color(css, "success"), _theme_color(css, "success_bg")
    ) >= 4.5
    assert _contrast_ratio(
        _theme_color(css, "error"), _theme_color(css, "error_bg")
    ) >= 4.5
