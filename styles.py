"""Vocogni visual system.

A quiet, high-clarity interface for learning: one type family, one primary
accent, restrained surfaces, consistent spacing, and strong focus states.
Theme, text scale, readability spacing, and motion remain learner-controlled.
"""
from string import Template


_CSS_TEMPLATE = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
    color-scheme: $color_scheme;
    --vc-bg: $bg;
    --vc-surface: $surface;
    --vc-surface-alt: $surface_alt;
    --vc-text: $text;
    --vc-subtext: $subtext;
    --vc-border: $border;
    --vc-accent: $accent;
    --vc-on-accent: $on_accent;
    --vc-apply: $apply_accent;
    --vc-success: $success;
    --vc-error: $error;
    --vc-success-bg: $success_bg;
    --vc-error-bg: $error_bg;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: var(--vc-bg) !important;
    color: var(--vc-text) !important;
    font-size: $base_px;
    line-height: $line_height;
}

[data-testid="stHeader"] {
    background: var(--vc-bg) !important;
    border-bottom: 1px solid transparent;
}

[data-testid="stAppViewContainer"] .main .block-container {
    max-width: 1160px;
    padding: 2.1rem clamp(1.1rem, 3.5vw, 2.8rem) 3.25rem;
}

[data-testid="stSidebar"] {
    background: var(--vc-surface) !important;
    border-right: 1px solid var(--vc-border);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.15rem 1rem 1.5rem;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
    color: var(--vc-text) !important;
}

[data-testid="stMarkdownContainer"] {
    color: var(--vc-text);
}

[data-testid="stMarkdownContainer"] p {
    line-height: $line_height;
    margin-bottom: 0.72rem;
}

h1, h2, h3, h4, .vc-heading {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--vc-text) !important;
    font-weight: 650 !important;
    letter-spacing: -0.035em;
    line-height: 1.2;
}

h1 { font-size: clamp(1.85rem, 3vw, 2.25rem) !important; margin: 0 0 0.7rem 0 !important; }
h2 { font-size: clamp(1.55rem, 2.5vw, 1.85rem) !important; margin: 0 0 0.65rem 0 !important; }
h3 { font-size: 1.22rem !important; margin: 1.25rem 0 0.6rem 0 !important; }
h4 { font-size: 1.02rem !important; margin: 0 0 0.5rem 0 !important; }

p, li, label, input, textarea, button, select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

a, [data-testid="stMarkdownContainer"] a {
    color: var(--vc-accent) !important;
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
}

a:hover, [data-testid="stMarkdownContainer"] a:hover {
    text-decoration-thickness: 2px;
}

.vc-muted,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: var(--vc-subtext) !important;
    font-size: 0.88rem;
}

.vc-page-intro {
    max-width: 760px;
    color: var(--vc-subtext);
    font-size: 1rem;
    line-height: 1.7;
    margin: 0.1rem 0 1.35rem 0;
}

.vc-eyebrow {
    color: var(--vc-subtext);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    line-height: 1.4;
    margin-bottom: 0.45rem;
    text-transform: uppercase;
}

hr, [data-testid="stDivider"] {
    border-color: var(--vc-border) !important;
}

.vc-logo-wrap {
    padding: 0.25rem 0 1.05rem 0;
    border-bottom: 1px solid var(--vc-border);
    margin-bottom: 1.05rem;
}

.vc-logo-row {
    align-items: center;
    display: flex;
    gap: 0.65rem;
}

.vc-logo-mark {
    align-items: center;
    background: var(--vc-accent);
    border-radius: 8px;
    color: var(--vc-on-accent);
    display: inline-flex;
    flex: 0 0 36px;
    font-size: 1.03rem;
    font-weight: 700;
    height: 36px;
    justify-content: center;
    letter-spacing: -0.04em;
    width: 36px;
}

.vc-logo-text {
    color: var(--vc-text);
    font-size: 1.23rem;
    font-weight: 700;
    letter-spacing: -0.055em;
    line-height: 1.15;
}

.vc-logo-tag {
    color: var(--vc-subtext);
    font-size: 0.7rem;
    line-height: 1.45;
    margin-top: 0.25rem;
}

.vc-card {
    background: var(--vc-surface);
    border: 1px solid var(--vc-border);
    border-radius: 10px;
    margin-bottom: 0.8rem;
    padding: 1rem 1.1rem;
}

.vc-card--apply { border-left: 3px solid var(--vc-apply); }
.vc-card--current { border-color: var(--vc-accent); }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--vc-surface) !important;
    border: 1px solid var(--vc-border) !important;
    border-radius: 11px !important;
}

.vc-badge {
    background: var(--vc-surface-alt);
    border: 1px solid var(--vc-border);
    border-radius: 6px;
    color: var(--vc-subtext);
    display: inline-block;
    font-size: 0.74rem;
    font-weight: 600;
    line-height: 1.45;
    margin-right: 0.25rem;
    padding: 0.18rem 0.48rem;
}

.vc-badge--apply { background: transparent; border-color: var(--vc-apply); color: var(--vc-apply); }
.vc-badge--success { background: var(--vc-success-bg); border-color: var(--vc-success-bg); color: var(--vc-success); }
.vc-badge--warn { background: var(--vc-error-bg); border-color: var(--vc-error-bg); color: var(--vc-error); }

.vc-stat-number {
    color: var(--vc-text);
    font-family: 'IBM Plex Mono', ui-monospace, monospace !important;
    font-size: 1.55rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    line-height: 1.25;
}

.vc-stat-label {
    color: var(--vc-subtext);
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 0.15rem;
}

.vc-lesson-row {
    background: var(--vc-surface);
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    margin-bottom: 0.55rem;
    padding: 0.8rem 0.95rem;
}

.vc-lesson-row--locked { opacity: 0.6; }
.vc-lesson-row--current { border-color: var(--vc-accent); }

.vc-summary-box,
.vc-challenge-box {
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    margin: 0.3rem 0 0.9rem;
    padding: 1rem 1.1rem;
    white-space: pre-wrap;
}

.vc-summary-box {
    background: var(--vc-surface-alt);
    border-left: 3px solid var(--vc-accent);
}

.vc-challenge-box {
    background: var(--vc-surface);
    border-left: 3px solid var(--vc-apply);
}

.vc-feedback {
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    margin: 0.6rem 0 0.9rem;
    padding: 0.85rem 1rem;
}

.vc-feedback--correct { background: var(--vc-success-bg); border-color: var(--vc-success-bg); }
.vc-feedback--incorrect { background: var(--vc-error-bg); border-color: var(--vc-error-bg); }

.vc-recommend-chip {
    background: var(--vc-surface-alt);
    border: 1px solid var(--vc-border);
    border-radius: 6px;
    color: var(--vc-text);
    display: inline-block;
    font-size: 0.82rem;
    margin: 0 0.35rem 0.35rem 0;
    padding: 0.28rem 0.58rem;
}

/* Consistent, low-noise controls */
.stButton > button,
.stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    box-shadow: none !important;
    font-size: 0.91rem !important;
    font-weight: 600 !important;
    min-height: 2.65rem;
    padding: 0.5rem 0.95rem;
    transition: $transition !important;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: var(--vc-accent) !important;
    border: 1px solid var(--vc-accent) !important;
    color: var(--vc-on-accent) !important;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(0.94);
}

.stButton > button[kind="secondary"],
.stFormSubmitButton > button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: var(--vc-surface) !important;
    border: 1px solid var(--vc-border) !important;
    color: var(--vc-text) !important;
}

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible,
input:focus-visible,
textarea:focus-visible {
    outline: 2px solid var(--vc-accent) !important;
    outline-offset: 2px !important;
}

[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100%;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-baseweb="select"] > div {
    background-color: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
    border-radius: 8px !important;
    color: var(--vc-text) !important;
}

[data-baseweb="select"] [data-testid="stMarkdownContainer"],
[data-baseweb="select"] span {
    color: var(--vc-text);
}

.stRadio label, .stCheckbox label, .stToggle label {
    font-size: 0.92rem;
}

[data-testid="stProgressBar"] > div {
    background: var(--vc-surface-alt) !important;
    border-radius: 999px;
    overflow: hidden;
}

[data-testid="stProgressBar"] > div > div {
    background: var(--vc-accent) !important;
    border-radius: 999px;
}

[data-testid="stExpander"] {
    background: var(--vc-surface);
    border: 1px solid var(--vc-border);
    border-radius: 10px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    font-weight: 600;
}

[data-testid="stAlert"] {
    border-radius: 9px;
}

[data-testid="stMetric"] {
    background: var(--vc-surface);
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    padding: 0.85rem 0.95rem;
}

[data-testid="stTabs"] button[role="tab"] {
    font-weight: 600;
}

table {
    border-color: var(--vc-border) !important;
}

* { scroll-behavior: $scroll_behavior; }

@media (max-width: 800px) {
    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 1.35rem 1rem 2.25rem;
    }
    .vc-stat-number { font-size: 1.35rem; }
    .vc-logo-wrap { margin-bottom: 0.65rem; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
""")


def build_css(settings: dict) -> str:
    """Render the visual system from the learner's current display settings."""
    dark = settings.get("appearance") == "Dark"

    size_map = {"Small": 14, "Medium": 16, "Large": 18}
    base_px = size_map.get(settings.get("text_size", "Medium"), 16)
    if settings.get("larger_text"):
        base_px = max(base_px, 19)

    line_height = 1.82 if settings.get("high_readability") else 1.62
    no_motion = (not settings.get("animations", True)) or settings.get("reduced_motion", False)

    if dark:
        tokens = dict(
            color_scheme="dark",
            on_accent="#10231F",
            bg="#101A20",
            surface="#18252C",
            surface_alt="#202F35",
            text="#F0F4F4",
            subtext="#A6B7BC",
            border="#33434A",
            accent="#63B8AA",
            apply_accent="#E0B66A",
            success="#84D5A6",
            error="#F08A7D",
            success_bg="#17382B",
            error_bg="#3E2524",
        )
    else:
        tokens = dict(
            color_scheme="light",
            on_accent="#FFFFFF",
            bg="#F6F8F9",
            surface="#FFFFFF",
            surface_alt="#F0F4F4",
            text="#182831",
            subtext="#5D6F76",
            border="#DFE7E9",
            accent="#176B64",
            apply_accent="#92651F",
            success="#247A50",
            error="#AF3F36",
            success_bg="#E9F5ED",
            error_bg="#FCEDEA",
        )

    tokens.update(
        base_px=f"{base_px}px",
        line_height=line_height,
        transition="none" if no_motion else "all 0.16s ease",
        scroll_behavior="auto" if no_motion else "smooth",
    )
    return _CSS_TEMPLATE.substitute(tokens)
