"""
styles.py — Visual design layer for VOCogni.

Design intent (Version 1):
  - Palette is a cool ink/paper base (not the common warm-cream-and-serif or
    near-black-neon look) with a single working accent — a deep teal used
    for every primary action and progress indicator, so it always means
    "go / progress." A second accent (warm amber) is reserved *only* for
    Real-World Challenge moments, so color itself signals "you are in the
    Apply stage" rather than decorating the page.
  - Two type families with distinct jobs: Space Grotesk for headings (a
    little technical/geometric, matching the "applied learning" brand),
    IBM Plex Sans for body and UI text (quiet and highly readable), and
    IBM Plex Mono used sparingly for stat numbers only, so progress reads
    like a measurement rather than a game score.
  - Structure comes from hairline borders, not stacked drop shadows; every
    card looks the same *unless* it's a Real-World Challenge (amber edge)
    or the current lesson (accent edge) — variation is informational.

Dark mode / text size / motion are implemented as a CSS layer generated at
runtime from Settings, since Streamlit does not expose a public API to
switch its native theme after the app has started. This is a solid
approximation for a prototype, not full native theming — see the README
"Known limitations" section.
"""

from string import Template

_CSS_TEMPLATE = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif !important;
    background-color: $bg !important;
    color: $text !important;
    font-size: ${base_px}px;
    line-height: $line_height;
}

[data-testid="stHeader"] { background-color: $bg !important; }

[data-testid="stSidebar"] { background-color: $surface !important; border-right: 1px solid $border; }

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: $text !important; }

[data-testid="stMarkdownContainer"] { color: $text; }

h1, h2, h3, h4, .vc-heading {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

.vc-muted { color: $subtext !important; font-size: 0.92em; }

hr { border-color: $border !important; }

.vc-logo-wrap {
    padding: 0.2rem 0 1rem 0;
    border-bottom: 1px solid $border;
    margin-bottom: 1rem;
}
.vc-logo-text {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: $text;
    letter-spacing: -0.02em;
}
.vc-logo-tag { color: $subtext; font-size: 0.76rem; margin-top: 0.15rem; }

.vc-card {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 10px;
    padding: 1.05rem 1.25rem;
    margin-bottom: 0.85rem;
    transition: $transition;
}
.vc-card--apply { border-left: 3px solid $apply_accent; }
.vc-card--current { border-color: $accent; box-shadow: 0 0 0 1px $accent; }

.vc-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    background-color: $surface_alt;
    color: $subtext;
    border: 1px solid $border;
}
.vc-badge--apply { background-color: transparent; border-color: $apply_accent; color: $apply_accent; }
.vc-badge--success { border-color: $success; color: $success; }
.vc-badge--warn { border-color: $error; color: $error; }

.vc-stat-number { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 1.65rem; color: $text; }
.vc-stat-label { color: $subtext; font-size: 0.8rem; margin-top: -0.25rem; }

.vc-lesson-row {
    padding: 0.7rem 0.9rem;
    border: 1px solid $border;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    background-color: $surface;
}
.vc-lesson-row--locked { opacity: 0.55; }
.vc-lesson-row--current { border-color: $accent; }

.vc-summary-box {
    background-color: $surface_alt;
    border: 1px solid $border;
    border-left: 3px solid $accent;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    white-space: pre-wrap;
    font-size: 0.96em;
}

.vc-challenge-box {
    background-color: $surface_alt;
    border: 1px solid $border;
    border-left: 3px solid $apply_accent;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    white-space: pre-wrap;
    margin-bottom: 1rem;
}

.vc-feedback { border-radius: 8px; padding: 0.85rem 1.1rem; margin: 0.6rem 0 0.9rem 0; border: 1px solid $border; }
.vc-feedback--correct { border-color: $success; background-color: $success_bg; }
.vc-feedback--incorrect { border-color: $error; background-color: $error_bg; }

.vc-recommend-chip {
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 8px;
    border: 1px solid $accent;
    color: $accent;
    background-color: $surface;
    font-size: 0.85rem;
    margin: 0 0.4rem 0.4rem 0;
}

.stButton > button { border-radius: 8px !important; transition: $transition !important; }
[data-testid="stSidebar"] .stButton > button { text-align: left !important; justify-content: flex-start !important; }

* { scroll-behavior: $scroll_behavior; }
</style>
""")


def build_css(settings: dict) -> str:
    """Render the full <style> block for the current Settings state."""
    dark = settings.get("appearance") == "Dark"

    size_map = {"Small": 14, "Medium": 16, "Large": 18}
    base_px = size_map.get(settings.get("text_size", "Medium"), 16)
    if settings.get("larger_text"):
        base_px = max(base_px, 19)

    line_height = 1.8 if settings.get("high_readability") else 1.55
    no_motion = (not settings.get("animations", True)) or settings.get("reduced_motion", False)

    if dark:
        tokens = dict(
            bg="#121A20", surface="#1B262C", surface_alt="#202D33",
            text="#E8EDEC", subtext="#9FB2B2", border="#2B3940",
            accent="#2E8C8C", apply_accent="#D9A046",
            success="#3FAE72", error="#DD6656",
            success_bg="#173226", error_bg="#3A2220",
        )
    else:
        tokens = dict(
            bg="#F5F7F7", surface="#FFFFFF", surface_alt="#EEF2F2",
            text="#16212C", subtext="#5A6B72", border="#DEE4E7",
            accent="#1C6B6B", apply_accent="#B8842E",
            success="#2F8F5B", error="#C0483D",
            success_bg="#E6F4EC", error_bg="#FBEAE8",
        )

    tokens.update(
        base_px=base_px,
        line_height=line_height,
        transition="none" if no_motion else "all 0.15s ease",
        scroll_behavior="auto" if no_motion else "smooth",
    )
    return _CSS_TEMPLATE.substitute(tokens)