"""Accessible, bilingual Terms of Service for Vocogni.

The document is intentionally marked as a draft until operator details, a
Privacy Notice, and applicable child-safety/consent mechanisms are completed.
"""
from __future__ import annotations

from pathlib import Path
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
TERMS_PATH = ROOT / "TERMS_OF_SERVICE.md"
ENGLISH_START = "<!-- ENGLISH_START -->"
INDONESIAN_START = "<!-- INDONESIAN_START -->"
END_MARKER = "<!-- END_TERMS -->"

DRAFT_NOTICE_EN = (
    "Draft for legal review. Before public launch, complete the operator's "
    "legal identity and contact details, publish a separate Privacy Notice, "
    "implement applicable age-suitability and parent/guardian consent "
    "safeguards, and obtain review from qualified Indonesian counsel. "
    "Displaying this page alone does not establish legal compliance."
)
DRAFT_NOTICE_ID = (
    "Draf untuk peninjauan hukum. Sebelum peluncuran publik, lengkapi "
    "identitas hukum dan kontak penyelenggara, terbitkan Pemberitahuan "
    "Privasi terpisah, terapkan perlindungan kesesuaian usia serta "
    "persetujuan orang tua/wali yang berlaku, dan minta peninjauan dari "
    "penasihat hukum Indonesia yang kompeten. Menampilkan halaman ini saja "
    "tidak membuktikan kepatuhan hukum."
)


def _read_terms() -> str:
    """Read the canonical version-controlled terms document."""
    try:
        return TERMS_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_language(document: str, language: str) -> str:
    """Return one language section, or a safe message if the file is missing."""
    if not document:
        return (
            "Ketentuan layanan belum tersedia." if language == "Bahasa Indonesia"
            else "The Terms of Service document is currently unavailable."
        )

    if language == "Bahasa Indonesia":
        start_marker, end_marker = INDONESIAN_START, END_MARKER
    else:
        start_marker, end_marker = ENGLISH_START, INDONESIAN_START

    if start_marker not in document or end_marker not in document:
        return (
            "Ketentuan layanan tidak dapat dimuat. Silakan coba lagi nanti."
            if language == "Bahasa Indonesia"
            else "The Terms of Service could not be loaded. Please try again later."
        )

    return document.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()


def _language_picker(key: str) -> str:
    return st.radio(
        "Bahasa / Language",
        options=["Bahasa Indonesia", "English"],
        horizontal=True,
        key=key,
        label_visibility="collapsed",
    )


def render_embedded() -> None:
    """Make the terms readable before sign-in without implying acceptance."""
    with st.expander("Ketentuan Layanan / Terms of Service — draft", expanded=False):
        language = _language_picker("terms_language_prelogin")
        st.warning(DRAFT_NOTICE_ID if language == "Bahasa Indonesia" else DRAFT_NOTICE_EN)
        st.markdown(_extract_language(_read_terms(), language))


def render() -> None:
    """Render the dedicated Terms page for authenticated learners."""
    language = _language_picker("terms_language")
    st.warning(DRAFT_NOTICE_ID if language == "Bahasa Indonesia" else DRAFT_NOTICE_EN)
    st.markdown(_extract_language(_read_terms(), language))
    st.divider()
    if language == "Bahasa Indonesia":
        st.caption(
            "Rujukan dan daftar kesiapan peluncuran untuk pengelola tersedia "
            "di docs/LEGAL_LAUNCH_CHECKLIST.md."
        )
    else:
        st.caption(
            "References and the operator's launch-readiness checklist are in "
            "docs/LEGAL_LAUNCH_CHECKLIST.md."
        )
