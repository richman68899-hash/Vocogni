"""Vocogni visual system.

A restrained, high-clarity interface for learning. Learners can personalize
type, accent colour, surface tone, corner shape, scale, spacing, and motion
without changing the learning content or durable progress model.
"""
import re
from string import Template


_CSS_TEMPLATE = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Source+Serif+4:wght@400;500;600;700&display=swap');

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
    --vc-nav-active-bg: $nav_active_bg;
    --vc-nav-active-text: $nav_active_text;
    --vc-font-family: $font_family;
    --vc-heading-font-family: $heading_font_family;
    --vc-radius-control: $radius_control;
    --vc-radius-card: $radius_card;
}

body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: var(--vc-font-family) !important;
    background: var(--vc-bg) !important;
    color: var(--vc-text) !important;
    font-size: 16px;
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
    font-family: var(--vc-heading-font-family) !important;
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
    font-family: var(--vc-font-family) !important;
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
    font-family: var(--vc-font-family) !important;
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

/* Optional, restrained wrong-answer motion: only attached when the learner enables it. */
@keyframes vc-answer-shake {
    0%, 100% { transform: translateX(0); }
    18%, 54%, 82% { transform: translateX(-3px); }
    36%, 70%, 92% { transform: translateX(3px); }
}
.vc-feedback--shake {
    animation: vc-answer-shake 280ms ease-in-out both;
}
@media (prefers-reduced-motion: reduce) {
    .vc-feedback--shake { animation: none !important; }
}

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

/* Refined product layer: restrained surfaces, clear hierarchy, predictable controls. */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}

::selection {
    background: var(--vc-accent);
    color: var(--vc-on-accent);
}

[data-testid="stAppViewContainer"] .main .block-container {
    max-width: 1120px;
    padding-top: 2rem;
}

h1, h2, h3, h4, .vc-heading {
    font-family: var(--vc-heading-font-family) !important;
    font-weight: 650 !important;
    letter-spacing: -0.028em;
}

h1 { margin-bottom: 0.55rem !important; }
h2 { margin-bottom: 0.55rem !important; }
h3 { margin-top: 1.05rem !important; }

.vc-page-intro {
    max-width: 700px;
    font-size: 0.98rem;
    line-height: 1.68;
    margin: 0.15rem 0 1.55rem;
}

.vc-eyebrow {
    letter-spacing: 0.075em;
    font-size: 0.69rem;
}

.vc-card,
.vc-lesson-row,
.vc-summary-box,
.vc-challenge-box,
.vc-feedback,
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stMetric"],
[data-testid="stExpander"] {
    box-shadow: none !important;
}

.vc-card,
.vc-lesson-row,
.vc-summary-box,
.vc-challenge-box,
.vc-feedback {
    border-radius: 9px;
}

.vc-card {
    padding: 1.05rem 1.1rem;
}

.vc-stat-number {
    font-size: 1.5rem;
    font-weight: 650;
    letter-spacing: -0.035em;
    font-variant-numeric: tabular-nums;
}

.vc-stat-label {
    font-size: 0.8rem;
    font-weight: 500;
}

.stButton > button,
.stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button {
    min-height: 2.55rem;
    border-radius: 7px !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(0.96);
}

[data-testid="stSidebar"] .stButton > button {
    min-height: 2.45rem;
    margin: 0.08rem 0;
    border-radius: 7px !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: var(--vc-nav-active-bg) !important;
    border-color: transparent !important;
    color: var(--vc-nav-active-text) !important;
    font-weight: 650 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-baseweb="select"] > div {
    min-height: 2.65rem;
    border-radius: 7px !important;
}

[data-testid="stMetric"] {
    border-radius: 9px;
    padding: 0.9rem 1rem;
}

[data-testid="stExpander"] summary {
    padding-top: 0.1rem;
    padding-bottom: 0.1rem;
}

[data-testid="stAlert"] {
    border: 1px solid var(--vc-border);
    box-shadow: none;
}

[data-testid="stProgressBar"] {
    padding: 0;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="radio"]:focus-visible {
    outline-color: var(--vc-accent) !important;
}

@media (max-width: 800px) {
    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 1.25rem 0.9rem 2rem;
    }
    .vc-page-intro {
        font-size: 0.94rem;
        margin-bottom: 1.2rem;
    }
}


/* ---------------------------------------------------------------
   VOCGONI PRODUCT FINISH
   A restrained editorial system: clear hierarchy, calm surfaces,
   deliberate spacing and accessible interaction states.
   --------------------------------------------------------------- */
.vc-page-intro {
    max-width: 680px;
    color: var(--vc-subtext) !important;
    font-size: 1rem;
    line-height: 1.72;
    margin: 0.15rem 0 1.65rem;
}
h1, h2, h3, h4, .vc-heading {
    font-family: var(--vc-heading-font-family) !important;
    letter-spacing: -0.035em;
    line-height: 1.22;
}
h1 { font-size: clamp(1.9rem, 3vw, 2.35rem) !important; font-weight: 750 !important; }
h2 { font-size: clamp(1.55rem, 2.5vw, 1.85rem) !important; font-weight: 700 !important; }
h3 { font-size: 1.16rem !important; font-weight: 700 !important; }
h4 { font-size: 1rem !important; font-weight: 700 !important; }
.vc-eyebrow {
    color: var(--vc-subtext);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.085em;
    margin-bottom: 0.5rem;
}
.vc-card, .vc-lesson-row, .vc-summary-box, .vc-challenge-box,
.vc-feedback, [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stMetric"], [data-testid="stExpander"] {
    box-shadow: none !important;
}
.vc-card, .vc-lesson-row, .vc-summary-box, .vc-challenge-box, .vc-feedback,
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"],
[data-testid="stExpander"] {
    border-radius: 10px !important;
}
.vc-card { padding: 1.15rem 1.2rem; }
.vc-card--current { border-color: var(--vc-border); border-left: 3px solid var(--vc-accent); }
.vc-stat-number {
    font-family: var(--vc-heading-font-family) !important;
    font-size: 1.55rem;
    font-weight: 750;
    letter-spacing: -0.04em;
}
.vc-stat-label { font-size: 0.78rem; line-height: 1.5; }
.stButton > button, .stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button {
    min-height: 2.65rem;
    border-radius: 8px !important;
    font-weight: 650 !important;
}
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: var(--vc-accent) !important;
    border-color: var(--vc-accent) !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(0.92);
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"],
.stFormSubmitButton > button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
}
[data-testid="stSidebar"] .stButton > button {
    min-height: 2.55rem;
    padding-left: 0.9rem;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: var(--vc-nav-active-bg) !important;
    border-color: transparent !important;
    color: var(--vc-nav-active-text) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] hr,
[data-testid="stSidebar"] hr { margin: 1rem 0; }
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-baseweb="select"] > div {
    border-radius: 8px !important;
}
[data-testid="stAlert"] {
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    box-shadow: none;
}
[data-testid="stProgressBar"] > div { background: var(--vc-surface-alt) !important; }
[data-testid="stProgressBar"] > div > div { background: var(--vc-accent) !important; }
[data-testid="stTabs"] button[role="tab"] { font-weight: 650; }
[data-testid="stCaptionContainer"] p { line-height: 1.55; }
::selection { background: var(--vc-accent); color: var(--vc-on-accent); }
@media (max-width: 800px) {
    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 1.25rem 0.9rem 2rem;
    }
    .vc-page-intro { font-size: 0.94rem; margin-bottom: 1.25rem; }
    .vc-card { padding: 0.95rem; }
}


/* ---------------------------------------------------------------
   CONTENT ALIGNMENT
   Keep icons optically centred with their labels and give key
   empty states and the sign-in entry a deliberate focal point.
   --------------------------------------------------------------- */
.vc-icon-text {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
    vertical-align: middle;
    line-height: 1.45;
}
.vc-icon-text__icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 1.15em;
    width: 1.15em;
    line-height: 1;
    vertical-align: middle;
}
.vc-status {
    align-items: center;
    display: inline-flex;
    gap: 0.4rem;
    line-height: 1.45;
    min-height: 1.35rem;
}
.vc-status__icon {
    align-items: center;
    display: inline-flex;
    flex: 0 0 1.15rem;
    height: 1.15rem;
    justify-content: center;
    line-height: 1;
    text-align: center;
}
.vc-status--complete { color: var(--vc-success); }
.vc-status--locked { color: var(--vc-subtext); }

/* Native Streamlit icon-bearing controls should share a baseline. */
.stButton > button,
.stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button {
    align-items: center !important;
    display: flex !important;
    gap: 0.42rem;
    justify-content: center;
}
.stButton > button [data-testid="stIconMaterial"],
.stFormSubmitButton > button [data-testid="stIconMaterial"],
[data-testid="stDownloadButton"] > button [data-testid="stIconMaterial"] {
    align-items: center;
    display: inline-flex;
    flex-shrink: 0;
    justify-content: center;
    line-height: 1;
    margin: 0;
}
.stButton > button svg,
.stFormSubmitButton > button svg,
[data-testid="stDownloadButton"] > button svg {
    display: block;
    flex-shrink: 0;
}
[data-testid="stAlert"] [data-testid="stIconMaterial"] {
    align-self: center;
    flex-shrink: 0;
    margin-top: 0;
}
[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start !important;
}

/* Sign-in is the one screen where a centred composition is appropriate. */
.vc-login-hero {
    margin: 0 auto 1.1rem;
    max-width: 34rem;
    text-align: center;
}
.vc-login-hero h1 {
    margin-bottom: 0.7rem !important;
}
.vc-login-hero .vc-page-intro {
    margin-left: auto;
    margin-right: auto;
}

/* Milestone icon, title and date use the same vertical centre line. */
.vc-milestone-icon {
    align-items: center;
    display: flex;
    font-size: 2.2rem;
    justify-content: center;
    line-height: 1;
    min-height: 3.2rem;
    text-align: center;
}
.vc-milestone-title {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.22rem;
    min-height: 3.2rem;
}
.vc-milestone-name {
    font-size: 1.08rem;
    font-weight: 700;
    line-height: 1.3;
    overflow-wrap: anywhere;
}
.vc-milestone-section {
    font-size: 0.82rem;
    font-weight: 600;
    line-height: 1.4;
}
.vc-milestone-date {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    justify-content: center;
    min-height: 3.2rem;
    text-align: right;
}
.vc-milestone-date-label {
    color: var(--vc-subtext);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    line-height: 1.3;
}
.vc-milestone-date-value {
    font-size: 0.88rem;
    font-weight: 650;
    line-height: 1.4;
    font-variant-numeric: tabular-nums;
}
.vc-checklist-item-text {
    align-items: center;
    display: flex;
    line-height: 1.5;
    min-height: 2.6rem;
    overflow-wrap: anywhere;
    padding: 0.1rem 0;
}
.vc-empty-state {
    align-items: center;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding: 2rem 1rem;
    text-align: center;
}
.vc-empty-state strong {
    font-size: 1.03rem;
    line-height: 1.4;
}
.vc-empty-state p {
    color: var(--vc-subtext);
    margin: 0;
    max-width: 32rem;
    line-height: 1.6;
}
@media (max-width: 800px) {
    .vc-milestone-date {
        align-items: flex-start;
        min-height: 0;
        margin-top: 0.4rem;
        text-align: left;
    }
    .vc-milestone-icon {
        min-height: 2.7rem;
    }
    .vc-milestone-title {
        min-height: 2.7rem;
    }
    .vc-checklist-item-text {
        min-height: 2.8rem;
    }
}


/* ------------------------------------------------------------------
   THEME CONTRAST PATCH
   Keep native Streamlit/BaseWeb controls in sync with the selected
   learner theme. The app supports a user-selected theme, so do not
   rely on Streamlit's static .streamlit/config.toml theme alone.
   ------------------------------------------------------------------ */
html {
    color-scheme: $color_scheme;
}
.stApp {
    --background-color: var(--vc-bg);
    --secondary-background-color: var(--vc-surface);
    --text-color: var(--vc-text);
    --primary-color: var(--vc-accent);
    --border-color: var(--vc-border);
    --code-background-color: var(--vc-surface-alt);
    --input-background-color: var(--vc-surface);
    color: var(--vc-text) !important;
    background: var(--vc-bg) !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    background-color: var(--vc-bg) !important;
    color: var(--vc-text) !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: var(--vc-surface) !important;
    color: var(--vc-text) !important;
}
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] blockquote,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stMarkdownContainer"] del,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label,
[data-testid="stToggle"] label,
[data-testid="stFileUploader"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSlider"] label,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"],
[data-testid="stExpander"] summary {
    color: var(--vc-text) !important;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
.stCaption,
.vc-muted {
    color: var(--vc-subtext) !important;
}
[data-testid="stMarkdownContainer"] a,
[data-testid="stLinkButton"] a {
    color: var(--vc-accent) !important;
}
[data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stExpander"],
[data-testid="stAlert"] {
    background-color: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stAlert"] p,
[data-testid="stAlert"] li {
    color: var(--vc-text) !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: var(--vc-surface-alt) !important;
}
[data-testid="stExpander"] svg,
[data-testid="stExpander"] summary span {
    color: var(--vc-text) !important;
}
.stApp button[data-testid="stBaseButton-tertiary"] {
    background: transparent !important;
    border-color: transparent !important;
    color: var(--vc-text) !important;
}
.stApp button[data-testid^="stBaseButton-"]:disabled {
    color: var(--vc-subtext) !important;
    opacity: 0.72;
}
.stApp input:not([type="checkbox"]):not([type="radio"]),
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea,
.stApp [data-testid="stNumberInput"] input,
.stApp [data-testid="stDateInput"] input,
.stApp [data-testid="stTimeInput"] input,
.stApp [data-baseweb="select"] > div {
    background-color: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
    color: var(--vc-text) !important;
    caret-color: var(--vc-accent);
}
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: var(--vc-subtext) !important;
    opacity: 1 !important;
}
.stApp input:focus,
.stApp textarea:focus,
.stApp [data-baseweb="input"] > div:focus-within,
.stApp [data-baseweb="textarea"] > div:focus-within {
    border-color: var(--vc-accent) !important;
    box-shadow: 0 0 0 1px var(--vc-accent) !important;
}
.stApp input[type="checkbox"],
.stApp input[type="radio"],
.stApp input[type="range"] {
    accent-color: var(--vc-accent) !important;
}
.stApp [data-baseweb="select"] span,
.stApp [data-baseweb="select"] input,
.stApp [data-baseweb="select"] [role="combobox"] {
    color: var(--vc-text) !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stMultiSelect"] [role="listbox"],
[data-testid="stMultiSelect"] [role="option"] {
    background-color: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
    color: var(--vc-text) !important;
}
[role="listbox"] [role="option"],
[role="menu"] [role="menuitem"],
[data-baseweb="menu"] [role="option"] {
    color: var(--vc-text) !important;
}
[role="listbox"] [role="option"]:hover,
[role="listbox"] [role="option"][aria-selected="true"],
[role="menu"] [role="menuitem"]:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: var(--vc-surface-alt) !important;
    color: var(--vc-text) !important;
}
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-color: var(--vc-border) !important;
}
.stApp table,
.stApp thead,
.stApp tbody,
.stApp tr,
.stApp th,
.stApp td {
    border-color: var(--vc-border) !important;
}
.stApp th {
    background-color: var(--vc-surface-alt) !important;
    color: var(--vc-text) !important;
}
.stApp td {
    background-color: var(--vc-surface) !important;
    color: var(--vc-text) !important;
}
.stApp pre,
.stApp code {
    background-color: var(--vc-surface-alt);
    color: var(--vc-text);
    border-color: var(--vc-border);
}
.stApp hr,
[data-testid="stDivider"] {
    border-color: var(--vc-border) !important;
}
.stApp ::selection {
    background: var(--vc-accent);
    color: var(--vc-on-accent);
}


/* Date/time popovers and multi-select chips also need runtime theme colours. */
[data-baseweb="calendar"],
[data-baseweb="calendar"] div,
[data-baseweb="calendar"] span,
[data-baseweb="calendar"] button,
[data-baseweb="timepicker"],
[data-baseweb="timepicker"] button {
    color: var(--vc-text) !important;
    border-color: var(--vc-border) !important;
}

[data-baseweb="calendar"] button:hover,
[data-baseweb="timepicker"] button:hover {
    background-color: var(--vc-surface-alt) !important;
}

[data-baseweb="calendar"] [aria-selected="true"],
[data-baseweb="calendar"] button[aria-pressed="true"] {
    background-color: var(--vc-accent) !important;
    color: var(--vc-on-accent) !important;
}

[data-baseweb="tag"] {
    background-color: var(--vc-surface-alt) !important;
    border: 1px solid var(--vc-border) !important;
    color: var(--vc-text) !important;
}

[data-baseweb="tag"] span {
    color: var(--vc-text) !important;
}

[data-baseweb="tag"] svg {
    color: var(--vc-subtext) !important;
}

/* Learner-selected personalization, applied after component defaults. */
.vc-card, .vc-lesson-row, .vc-summary-box, .vc-challenge-box, .vc-feedback,
.vc-badge, .vc-recommend-chip,
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"],
[data-testid="stExpander"], [data-testid="stAlert"] {
    border-radius: var(--vc-radius-card) !important;
}
.stButton > button, .stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button,
.stApp input:not([type="checkbox"]):not([type="radio"]),
.stApp textarea, .stApp [data-baseweb="select"] > div {
    border-radius: var(--vc-radius-control) !important;
}

/* Profile page: restrained identity, section icons, and easy-to-scan details. */
.vc-profile-page-heading { margin-bottom: 1.15rem; }
.vc-profile-page-heading h1 { margin-top: 0.12rem !important; }
.vc-profile-hero {
    align-items: center;
    background: var(--vc-surface);
    border: 1px solid var(--vc-border);
    border-radius: 12px;
    display: flex;
    gap: 1rem;
    min-height: 112px;
    padding: 1.15rem 1.25rem;
}
.vc-profile-avatar {
    align-items: center;
    background: var(--vc-nav-active-bg);
    border: 1px solid color-mix(in srgb, var(--vc-accent) 24%, var(--vc-border));
    border-radius: 50%;
    color: var(--vc-nav-active-text);
    display: flex;
    flex: 0 0 64px;
    font-size: 1.2rem;
    font-weight: 700;
    height: 64px;
    justify-content: center;
    letter-spacing: -0.035em;
    width: 64px;
}
.vc-profile-identity-copy { min-width: 0; }
.vc-profile-name {
    color: var(--vc-text);
    font-size: 1.28rem;
    font-weight: 650;
    letter-spacing: -0.035em;
    line-height: 1.25;
    overflow-wrap: anywhere;
}
.vc-profile-identity-subtitle {
    color: var(--vc-subtext);
    font-size: 0.87rem;
    line-height: 1.5;
    margin: 0.22rem 0 0.55rem;
}
.vc-profile-status {
    align-items: center;
    color: var(--vc-success);
    display: inline-flex;
    font-size: 0.75rem;
    font-weight: 600;
    gap: 0.32rem;
}
.vc-profile-status--quiet { color: var(--vc-subtext); }
.vc-profile-status .vc-profile-icon-art { height: 14px; width: 14px; }
.vc-profile-section-heading {
    align-items: flex-start;
    display: flex;
    gap: 0.75rem;
    margin: 0.1rem 0 1.15rem;
}
.vc-profile-section-icon, .vc-profile-empty-icon {
    align-items: center;
    background: var(--vc-surface-alt);
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    color: var(--vc-accent);
    display: inline-flex;
    flex: 0 0 38px;
    height: 38px;
    justify-content: center;
    width: 38px;
}
.vc-profile-icon-art { display: block; height: 20px; width: 20px; }
.vc-profile-section-copy { min-width: 0; padding-top: 0.05rem; }
.vc-profile-section-title {
    color: var(--vc-text);
    font-size: 1.02rem;
    font-weight: 650;
    letter-spacing: -0.018em;
    line-height: 1.35;
}
.vc-profile-section-subtitle {
    color: var(--vc-subtext);
    font-size: 0.84rem;
    line-height: 1.45;
    margin: 0.16rem 0 0 !important;
}
.vc-profile-field {
    border-bottom: 1px solid var(--vc-border);
    margin: 0 0 0.85rem;
    min-height: 3.3rem;
    padding: 0 0 0.7rem;
    overflow-wrap: anywhere;
}
.vc-profile-field-label {
    color: var(--vc-subtext);
    font-size: 0.77rem;
    font-weight: 500;
    line-height: 1.45;
    margin-bottom: 0.25rem;
}
.vc-profile-field-value {
    color: var(--vc-text);
    font-size: 0.91rem;
    font-weight: 550;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}
.vc-profile-value--empty {
    color: var(--vc-subtext);
    font-size: 0.83rem;
    font-weight: 400;
    font-style: italic;
}
.vc-profile-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.vc-profile-tag {
    background: var(--vc-surface-alt);
    border: 1px solid var(--vc-border);
    border-radius: 6px;
    color: var(--vc-text);
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 500;
    line-height: 1.35;
    padding: 0.22rem 0.48rem;
}
.vc-profile-empty { padding: 1rem 0.2rem 0.8rem; }
.vc-profile-empty-icon { margin-bottom: 0.8rem; }
.vc-profile-empty-title {
    color: var(--vc-text);
    font-size: 1.05rem;
    font-weight: 650;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.vc-profile-empty-copy {
    color: var(--vc-subtext);
    font-size: 0.91rem;
    line-height: 1.6;
    margin: 0 0 0.9rem !important;
    max-width: 580px;
}
.vc-profile-form-note {
    align-items: flex-start;
    background: var(--vc-surface-alt);
    border: 1px solid var(--vc-border);
    border-radius: 9px;
    color: var(--vc-subtext);
    display: flex;
    font-size: 0.85rem;
    gap: 0.65rem;
    line-height: 1.55;
    margin: 0 0 1rem;
    padding: 0.8rem 0.9rem;
}
.vc-profile-form-note .vc-profile-icon-art {
    color: var(--vc-accent);
    flex: 0 0 18px;
    height: 18px;
    margin-top: 0.1rem;
    width: 18px;
}
.vc-profile-form-note strong { color: var(--vc-text); }
[data-testid="stVerticalBlockBorderWrapper"]:has(.vc-profile-section-heading) {
    padding: 1.1rem 1.15rem 0.25rem;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.vc-profile-empty) {
    padding: 1.2rem 1.4rem;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.vc-profile-section-heading) + [data-testid="stVerticalBlockBorderWrapper"] {
    margin-top: 0.1rem;
}
@media (max-width: 760px) {
    .vc-profile-hero { gap: 0.8rem; padding: 0.95rem; }
    .vc-profile-avatar { flex-basis: 52px; height: 52px; width: 52px; font-size: 1.05rem; }
    .vc-profile-name { font-size: 1.12rem; }
    .vc-profile-identity-subtitle { font-size: 0.82rem; }
    .vc-profile-section-heading { gap: 0.6rem; margin-bottom: 0.9rem; }
    .vc-profile-section-icon, .vc-profile-empty-icon { flex-basis: 34px; height: 34px; width: 34px; }
    .vc-profile-field { min-height: 0; }
}


/* Select controls: keep the value area, caret area, and label legible in
   both themes. BaseWeb paints the dropdown indicator separately from the
   control surface, which can otherwise leave a bright block in dark mode. */
.stApp [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {
    display: block !important;
    height: auto !important;
    min-height: 1.25rem;
    margin-bottom: 0.3rem !important;
    overflow: visible !important;
}
.stApp [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] label {
    display: inline-block !important;
    height: auto !important;
    line-height: 1.4 !important;
    overflow: visible !important;
    visibility: visible !important;
    color: var(--vc-text) !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: var(--vc-surface) !important;
    border-color: var(--vc-border) !important;
    color: var(--vc-text) !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div * {
    background-color: transparent !important;
    color: var(--vc-text) !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div svg {
    color: var(--vc-text) !important;
    fill: currentColor !important;
    stroke: currentColor !important;
}


/* ------------------------------------------------------------------
   RESPONSIVE LAYOUT REPAIR
   Compact navigation and reclaim the available canvas, especially on
   tablets in landscape. Keep mobile's collapsible sidebar behaviour.
   ------------------------------------------------------------------ */
@media (min-width: 900px) {
    section[data-testid="stSidebar"][aria-expanded="true"] {
        width: 17.25rem !important;
        min-width: 17.25rem !important;
        max-width: 17.25rem !important;
        flex-shrink: 0 !important;
    }

    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] .main .block-container {
        width: 100% !important;
        max-width: 1320px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 1.35rem clamp(1rem, 2.5vw, 2.15rem) 2.8rem !important;
        box-sizing: border-box !important;
    }
}

/* Reduce the large gaps between persistent navigation actions. */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.62rem !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] hr,
section[data-testid="stSidebar"] hr {
    margin: 0.75rem 0 !important;
}

section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button[data-testid^="stBaseButton-"] {
    box-sizing: border-box !important;
    height: auto !important;
    min-height: 2.25rem !important;
    padding: 0.28rem 0.72rem !important;
    line-height: 1.25 !important;
    font-size: 0.9rem !important;
    border-radius: 8px !important;
    margin: 0 !important;
}

.stButton > button,
.stFormSubmitButton > button,
[data-testid="stDownloadButton"] > button {
    box-sizing: border-box !important;
    height: auto !important;
    min-height: 2.45rem !important;
    padding: 0.38rem 0.85rem !important;
    line-height: 1.25 !important;
    white-space: normal !important;
}

/* Constrain controls and prevent layout overflow in tablet-sized viewports. */
.stApp [data-testid="stSelectbox"],
.stApp [data-testid="stMultiSelect"],
.stApp [data-testid="stTextInput"],
.stApp [data-testid="stNumberInput"],
.stApp [data-testid="stTextArea"] {
    min-width: 0 !important;
}

.stApp [data-testid="stHorizontalBlock"] {
    min-width: 0;
}

@media (max-width: 1100px) {
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] .main .block-container {
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
    }

    .stApp [data-testid="stHorizontalBlock"] {
        gap: 0.65rem !important;
    }
}

@media (max-width: 760px) {
    section[data-testid="stSidebar"][aria-expanded="true"] {
        width: min(18rem, 88vw) !important;
        min-width: min(18rem, 88vw) !important;
        max-width: min(18rem, 88vw) !important;
    }

    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 1rem 0.85rem 2rem !important;
    }

    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="stDownloadButton"] > button {
        min-height: 2.35rem !important;
    }
}

/* ------------------------------------------------------------------
   TEXT-SIZE REFLOW
   Text size is a typographic preference, not a page zoom. Keep the
   document's rem baseline stable and let labels wrap instead of forcing
   controls, columns, and cards wider than their available space.
   ------------------------------------------------------------------ */
.stApp [data-testid="stHorizontalBlock"],
.stApp [data-testid="column"],
.stApp [data-testid="stVerticalBlock"],
.stApp [data-testid="stVerticalBlockBorderWrapper"],
.stApp [data-testid="stWidgetLabel"] {
    min-width: 0 !important;
    max-width: 100%;
}
.stApp [data-testid="stWidgetLabel"] label,
.stApp [data-testid="stWidgetLabel"] p {
    white-space: normal !important;
    overflow-wrap: anywhere;
    line-height: 1.4;
}
.stApp .stButton > button,
.stApp .stFormSubmitButton > button,
.stApp [data-testid="stDownloadButton"] > button,
.stApp [data-testid="stLinkButton"] > a {
    height: auto !important;
    max-width: 100%;
    white-space: normal !important;
    overflow-wrap: anywhere;
    word-break: normal;
}
.stApp .stButton > button > div,
.stApp .stFormSubmitButton > button > div,
.stApp [data-testid="stDownloadButton"] > button > div {
    min-width: 0;
    white-space: normal !important;
    overflow-wrap: anywhere;
}
.stApp [data-testid="stSelectbox"],
.stApp [data-testid="stMultiSelect"],
.stApp [data-testid="stTextInput"],
.stApp [data-testid="stNumberInput"],
.stApp [data-testid="stTextArea"],
.stApp [data-testid="stRadio"],
.stApp [data-testid="stCheckbox"],
.stApp [data-testid="stToggle"] {
    min-width: 0 !important;
    max-width: 100%;
}
.stApp [data-baseweb="select"] [role="combobox"] {
    min-width: 0;
    max-width: 100%;
    white-space: normal;
}
.vc-card, .vc-lesson-row, .vc-summary-box, .vc-challenge-box,
.vc-feedback, .vc-profile-identity-copy, .vc-profile-section-copy {
    min-width: 0;
    overflow-wrap: anywhere;
}
@media (max-width: 760px) {
    .stApp [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        align-items: stretch;
    }
    .stApp [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: min(100%, 15rem) !important;
    }
}



/* ---------------------------------------------------------------
   UI POLISH: unclipped card endings, readable sidebar, and stable
   catalog controls. Keep spacing in the document flow.
   --------------------------------------------------------------- */
[data-testid="stAppViewContainer"] .main .block-container {
    padding-bottom: 4.5rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    padding-bottom: 0.55rem !important;
    margin-bottom: 0.8rem !important;
}
.vc-course-progress-label {
    display: block;
    margin: 0.4rem 0 0.35rem;
    padding-bottom: 0.25rem;
    line-height: 1.55;
    min-height: 1.6rem;
    overflow-wrap: anywhere;
}
.vc-sidebar-tagline {
    color: var(--vc-subtext);
    font-size: 0.76rem;
    font-weight: 500;
    line-height: 1.65;
    letter-spacing: 0.005em;
    margin: 0.65rem 0 0.55rem;
    padding: 0.1rem 0 0.15rem;
}
.vc-sidebar-tagline span {
    color: var(--vc-accent);
    padding: 0 0.1rem;
}
[data-testid="stSidebar"] hr.vc-sidebar-divider {
    margin: 0.6rem 0 1.05rem !important;
    opacity: 0.8;
}
[data-testid="stSidebar"] .stButton > button {
    line-height: 1.45 !important;
    margin-top: 0.16rem !important;
    margin-bottom: 0.2rem !important;
    padding-top: 0.62rem !important;
    padding-bottom: 0.62rem !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] hr {
    margin-top: 1.15rem !important;
    margin-bottom: 1.15rem !important;
}
[data-testid="stSidebar"] .vc-muted {
    line-height: 1.55;
}
@media (max-width: 800px) {
    [data-testid="stAppViewContainer"] .main .block-container {
        padding-bottom: 3.5rem !important;
    }
    .vc-course-progress-label {
        margin-bottom: 0.45rem;
    }
}

</style>
""")


def _hex_rgb(value: str) -> tuple[int, int, int]:
    """Parse a validated six-digit hexadecimal colour."""
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(channel))):02X}" for channel in rgb)


def _relative_luminance(value: str) -> float:
    channels = [channel / 255 for channel in _hex_rgb(value)]
    linear = [
        channel / 12.92 if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    high, low = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _contrast_safe_accent(value: str, surface: str, dark: bool) -> str:
    """Adjust a custom accent only as much as needed for readable links and controls."""
    if _contrast_ratio(value, surface) >= 4.5:
        return value
    original = _hex_rgb(value)
    target = (255, 255, 255) if dark else (0, 0, 0)
    for step in range(1, 101):
        amount = step / 100
        candidate = _rgb_hex(tuple(
            original[i] + (target[i] - original[i]) * amount
            for i in range(3)
        ))
        if _contrast_ratio(candidate, surface) >= 4.5:
            return candidate
    return _rgb_hex(target)


def _best_button_text(background: str) -> str:
    """Select whichever of white or deep ink has the stronger contrast."""
    light = "#FFFFFF"
    dark = "#14241F"
    return light if _contrast_ratio(light, background) >= _contrast_ratio(dark, background) else dark


def _tint(surface: str, accent: str, amount: float) -> str:
    base_rgb, accent_rgb = _hex_rgb(surface), _hex_rgb(accent)
    return _rgb_hex(tuple(base_rgb[i] * (1 - amount) + accent_rgb[i] * amount for i in range(3)))



_FONT_SIZE_DECLARATION = re.compile(r"(?<![\w-])font-size\s*:\s*([^;]+);")
_FONT_SIZE_LENGTH = re.compile(r"(?<![\w.-])(\d+(?:\.\d+)?)(rem|px|vw|pt)\b")


def _scale_css_font_sizes(css: str, scale: float) -> str:
    """Scale declared text sizes without scaling rem-based layout spacing.

    Streamlit's text-size setting is a typography preference, not a layout
    zoom. Scaling the root font size also widens rem-based sidebars and
    increases padding, which can cause columns and controls to overflow.
    """
    if abs(scale - 1.0) < 1e-9:
        return css

    def scale_declaration(match: re.Match[str]) -> str:
        value = match.group(1)

        def scale_length(length_match: re.Match[str]) -> str:
            amount = float(length_match.group(1)) * scale
            rendered = f"{amount:.4f}".rstrip("0").rstrip(".")
            return f"{rendered}{length_match.group(2)}"

        scaled_value = _FONT_SIZE_LENGTH.sub(scale_length, value)
        return f"font-size: {scaled_value};"

    return _FONT_SIZE_DECLARATION.sub(scale_declaration, css)

def build_css(settings: dict) -> str:
    """Render the visual system from the learner's current display settings."""
    dark = settings.get("appearance") == "Dark"

    size_map = {"Small": 14, "Medium": 16, "Large": 18}
    base_px = size_map.get(settings.get("text_size", "Medium"), 16)
    if settings.get("larger_text"):
        base_px = max(base_px, 19)

    line_height = 1.82 if settings.get("high_readability") else 1.62
    no_motion = (not settings.get("animations", True)) or settings.get("reduced_motion", False)
    font_choices = {
        "Inter": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "Manrope": "'Manrope', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "Atkinson Hyperlegible": "'Atkinson Hyperlegible', 'Inter', sans-serif",
        "Source Serif 4": "'Source Serif 4', Georgia, serif",
    }
    font_family = font_choices.get(settings.get("font_family", "Inter"), font_choices["Inter"])
    background_tone = settings.get("background_tone", "Neutral")
    corner_style = settings.get("corner_style", "Standard")
    radius_choices = {
        "Standard": ("8px", "10px"),
        "Rounded": ("13px", "16px"),
        "Square": ("3px", "4px"),
    }
    radius_control, radius_card = radius_choices.get(corner_style, radius_choices["Standard"])

    if dark:
        tokens = dict(
            color_scheme="dark",
            on_accent="#14241F",
            bg="#101A17",
            surface="#17231E",
            surface_alt="#202D27",
            text="#F0F4F0",
            subtext="#B1BDB5",
            border="#34443B",
            accent="#79C8AD",
            apply_accent="#DDBB78",
            success="#8FD1A4",
            error="#F09A8E",
            success_bg="#1D382B",
            error_bg="#3B2725",
            nav_active_bg="#20372F",
            nav_active_text="#A6E0CC",
        )
    else:
        tokens = dict(
            color_scheme="light",
            on_accent="#FFFFFF",
            bg="#F7F8F5",
            surface="#FFFFFF",
            surface_alt="#EFF3EF",
            text="#1B2925",
            subtext="#586760",
            border="#DFE6E0",
            accent="#176B5B",
            apply_accent="#805A2A",
            success="#246B4A",
            error="#A53C36",
            success_bg="#EAF4ED",
            error_bg="#FCEFED",
            nav_active_bg="#E7F1EB",
            nav_active_text="#15594B",
        )

    # Optional surface palettes preserve the selected light/dark theme while
    # allowing a warmer paper-like canvas or a cooler blue-grey workspace.
    palettes = {
        "Light": {
            "Warm": dict(bg="#FAF7F2", surface="#FFFCF7", surface_alt="#F3EDE3", border="#E6DCCF", nav_active_bg="#EFE5D6", nav_active_text="#684B27"),
            "Cool": dict(bg="#F4F7FA", surface="#FFFFFF", surface_alt="#EAF0F6", border="#D9E3EC", nav_active_bg="#E0EAF3", nav_active_text="#254B69"),
        },
        "Dark": {
            "Warm": dict(bg="#181512", surface="#211D19", surface_alt="#2B251F", border="#463B31", nav_active_bg="#30271E", nav_active_text="#E4C8A0"),
            "Cool": dict(bg="#141920", surface="#1C242D", surface_alt="#252F3A", border="#364654", nav_active_bg="#263845", nav_active_text="#B7D9F2"),
        },
    }
    tone_palette = palettes.get("Dark" if dark else "Light", {}).get(background_tone)
    if tone_palette:
        tokens.update(tone_palette)

    if settings.get("use_custom_accent", False):
        selected = settings.get("custom_accent_color", "#176B5B")
        if not isinstance(selected, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", selected):
            selected = "#79C8AD" if dark else "#176B5B"
        # Keep customized colour legible on the chosen surface. Extreme light
        # or dark picks are nudged toward a WCAG AA contrast-safe shade.
        accent = _contrast_safe_accent(selected.upper(), tokens["surface"], dark)
        tokens["accent"] = accent
        tokens["on_accent"] = _best_button_text(accent)
        tokens["nav_active_bg"] = _tint(tokens["surface"], accent, 0.12 if dark else 0.08)
        tokens["nav_active_text"] = _contrast_safe_accent(
            accent, tokens["nav_active_bg"], dark
        )

    tokens.update(
        base_px=f"{base_px}px",
        line_height=line_height,
        transition="none" if no_motion else "all 0.16s ease",
        scroll_behavior="auto" if no_motion else "smooth",
        font_family=font_family,
        heading_font_family=font_family,
        radius_control=radius_control,
        radius_card=radius_card,
    )
    rendered_css = _CSS_TEMPLATE.substitute(tokens)
    # Keep rem units anchored to the browser's root size. Only typography is
    # scaled, so a learner selecting larger text doesn't also enlarge sidebar
    # widths, card padding, gaps, and other layout geometry.
    return _scale_css_font_sizes(rendered_css, base_px / 16.0)
