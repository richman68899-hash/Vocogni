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


def test_wrong_answer_shake_is_subtle_and_respects_reduced_motion():
    css = styles.build_css({"appearance": "Light"})
    assert ".vc-feedback--shake" in css
    assert "animation: vc-answer-shake 280ms ease-in-out both;" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "animation: none !important;" in css


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
    assert '.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div *' in css
    assert "min-height: 1.25rem;" in css
    assert "[data-testid=\"stAlert\"] p" in css
    assert "$" not in css


def test_light_theme_keeps_native_controls_theme_aware():
    css = styles.build_css({"appearance": "Light"})
    assert "color-scheme: light;" in css
    assert "--text-color: var(--vc-text);" in css
    assert "background-color: var(--vc-surface) !important;" in css
    assert "$" not in css



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


def test_dark_mode_text_colours_meet_wcag_aa_contrast():
    css = styles.build_css({"appearance": "Dark"})
    backgrounds = [
        _theme_color(css, "bg"),
        _theme_color(css, "surface"),
        _theme_color(css, "surface_alt"),
    ]

    # WCAG AA requires at least 4.5:1 for normal-sized text.
    for foreground_token in ("text", "subtext"):
        foreground = _theme_color(css, foreground_token)
        for background in backgrounds:
            assert _contrast_ratio(foreground, background) >= 4.5, (
                f"{foreground_token} contrast is too low on {background}"
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


def test_dark_mode_styles_calendar_and_multiselect_chip_text():
    css = styles.build_css({"appearance": "Dark"})
    assert '[data-baseweb="calendar"] button:hover' in css
    assert '[data-baseweb="calendar"] [aria-selected="true"]' in css
    assert '[data-baseweb="tag"] span' in css
    assert '[data-baseweb="tag"] svg' in css
    assert "$" not in css



def test_custom_appearance_preferences_change_the_rendered_css():
    css = styles.build_css({
        "appearance": "Dark",
        "font_family": "Source Serif 4",
        "background_tone": "Cool",
        "corner_style": "Rounded",
        "use_custom_accent": True,
        "custom_accent_color": "#FFF000",
    })
    assert "--vc-bg: #141920;" in css
    assert "--vc-font-family: 'Source Serif 4', Georgia, serif;" in css
    assert "--vc-heading-font-family: 'Source Serif 4', Georgia, serif;" in css
    assert "--vc-radius-control: 13px;" in css
    assert "--vc-radius-card: 16px;" in css
    assert "$" not in css


def test_custom_accent_is_adjusted_for_contrast_and_keeps_button_text_readable():
    css = styles.build_css({
        "appearance": "Light",
        "use_custom_accent": True,
        "custom_accent_color": "#FFFFFF",
    })
    accent = _theme_color(css, "accent")
    surface = _theme_color(css, "surface")
    button_text = _theme_color(css, "on_accent")
    nav_bg = _theme_color(css, "nav_active_bg")
    nav_text = _theme_color(css, "nav_active_text")
    assert _contrast_ratio(accent, surface) >= 4.5
    assert _contrast_ratio(button_text, accent) >= 4.5
    assert _contrast_ratio(nav_text, nav_bg) >= 4.5


def test_invalid_custom_accent_falls_back_safely():
    css = styles.build_css({
        "appearance": "Light",
        "use_custom_accent": True,
        "custom_accent_color": "javascript:alert(1)",
    })
    assert "--vc-accent: #176B5B;" in css
    assert "$" not in css


def test_tablet_layout_reclaims_space_and_compacts_navigation():
    css = styles.build_css({"appearance": "Dark"})
    assert 'section[data-testid="stSidebar"][aria-expanded="true"]' in css
    assert "width: 17.25rem !important;" in css
    assert "max-width: 1320px !important;" in css
    assert "min-height: 2.25rem !important;" in css
    assert "gap: 0.62rem !important;" in css
    assert "$" not in css


def test_select_arrow_and_control_use_theme_surface():
    css = styles.build_css({"appearance": "Dark"})
    assert '.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div *' in css
    assert "background-color: transparent !important;" in css
    assert "color: var(--vc-text) !important;" in css
    assert "$" not in css

def test_text_size_scales_type_without_scaling_layout_geometry():
    small = styles.build_css({"appearance": "Dark", "text_size": "Small"})
    medium = styles.build_css({"appearance": "Dark", "text_size": "Medium"})
    large = styles.build_css({
        "appearance": "Dark",
        "text_size": "Large",
        "larger_text": True,
    })

    # The body typography changes, but rem-based page geometry remains stable.
    assert "font-size: 14px;" in small
    assert "font-size: 16px;" in medium
    assert "font-size: 19px;" in large
    for css in (small, medium, large):
        assert "width: 17.25rem !important;" in css
        assert "padding: 1.15rem 1rem 1.5rem;" in css
        assert "min-width: 0 !important;" in css
        assert "white-space: normal !important;" in css
        assert "$" not in css


def test_large_text_scales_heading_and_control_typography():
    large = styles.build_css({
        "appearance": "Light",
        "text_size": "Large",
        "larger_text": True,
    })
    small = styles.build_css({"appearance": "Light", "text_size": "Small"})

    assert "font-size: clamp(2.2563rem, 3.5625vw, 2.7906rem) !important;" in large
    assert "font-size: clamp(1.6188rem, 2.625vw, 1.9688rem) !important;" in small
    assert "flex-wrap: wrap !important;" in large
    assert "overflow-wrap: anywhere;" in large

