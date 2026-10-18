"""Transparent, rubric-based open-ended answer scoring for Vocogni.

This is deterministic practice marking, not an official Cambridge examiner or
an unrestricted LLM judgement. Question authors define auditable mark points.
"""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


_SUBSCRIPT = str.maketrans({
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁺": "+", "⁻": "-", "−": "-", "×": "*", "·": "*",
    "→": "->", "⇌": "<->", "＝": "=",
})

# Accepted orthographic variants; they are not chemically different answers.
_VARIANTS = {
    "sulfate": {"sulphate"},
    "sulfite": {"sulphite"},
    "sulfur": {"sulphur"},
    "aluminium": {"aluminum"},
    "aluminum": {"aluminium"},
    "hydrogencarbonate": {"bicarbonate"},
    "ethanoate": {"acetate"},
    "tetroxide": {"tetraoxide"},
}
_DISTINCT_PAIRS = [
    ("sulfate", "sulfite"),
    ("nitrate", "nitrite"),
    ("phosphate", "phosphite"),
    ("chloride", "chlorate"),
    ("oxide", "peroxide"),
]


def normalize_notation(value: object) -> str:
    """Normalise typography while retaining a compact, searchable answer."""
    text = unicodedata.normalize("NFKC", str(value or "")).translate(_SUBSCRIPT)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", "", text)
    return text.casefold()


def normalize_words(value: object) -> str:
    """Normalise prose without changing the learner's original saved answer."""
    text = unicodedata.normalize("NFKC", str(value or "")).translate(_SUBSCRIPT)
    text = text.replace("→", "->").replace("−", "-").replace("⁻", "-").replace("⁺", "+")
    return re.sub(r"\s+", " ", text).strip().casefold()


def _expand_variants(value: str) -> set[str]:
    variants = {value}
    for preferred, alternatives in _VARIANTS.items():
        if preferred in value:
            variants.update(value.replace(preferred, alt) for alt in alternatives)
        for alt in alternatives:
            if alt in value:
                variants.add(value.replace(alt, preferred))
    return variants


def _contains_any(answer_text: str, compact_text: str, alternatives) -> bool:
    for alternative in alternatives or []:
        term = str(alternative).strip()
        if not term:
            continue
        prose_term = normalize_words(term)
        compact_term = normalize_notation(term)
        # Phrase/scientific-name matching is case insensitive. Formula and
        # equation variants are compacted to accept Unicode subscripts/arrows.
        if prose_term and prose_term in answer_text:
            return True
        if compact_term and any(v in compact_text for v in _expand_variants(compact_term)):
            return True
    return False


def _extract_numbers(raw: str) -> list[float]:
    # Avoid reading subscripts in H2, SO4, etc. as numerical working.
    pattern = r"(?<![A-Za-z0-9])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?(?![A-Za-z0-9])"
    out = []
    for match in re.finditer(pattern, raw.translate(_SUBSCRIPT)):
        try:
            out.append(float(match.group(0)))
        except ValueError:
            continue
    return out


def _point_matches(point: dict, raw: str, answer_text: str, compact_text: str, numbers: list[float]) -> bool:
    """All configured rule families must pass; alternatives within a family are OR."""
    configured = False

    if "match_any" in point:
        configured = True
        if not _contains_any(answer_text, compact_text, point.get("match_any", [])):
            return False

    if "match_groups" in point:
        configured = True
        groups = point.get("match_groups") or []
        if not all(_contains_any(answer_text, compact_text, group) for group in groups):
            return False

    if "regex_any" in point:
        configured = True
        patterns = point.get("regex_any") or []
        if not any(
            re.search(pattern, normalize_words(raw), flags=re.IGNORECASE)
            or re.search(pattern, compact_text, flags=re.IGNORECASE)
            for pattern in patterns
        ):
            return False

    if "numeric_targets" in point:
        configured = True
        targets = point.get("numeric_targets") or []
        numeric_ok = False
        for target in targets:
            try:
                expected = float(target["value"])
                tolerance = float(target.get("tolerance", 0.01))
            except (KeyError, TypeError, ValueError):
                continue
            if any(abs(value - expected) <= tolerance for value in numbers):
                numeric_ok = True
                break
        if not numeric_ok:
            return False

    return configured


def detect_typo_warnings(answer: object, question: dict) -> list[str]:
    """Warn about probable misspellings without auto-correcting or changing marks."""
    raw = str(answer or "")
    if not raw.strip():
        return []
    answer_words = re.findall(r"[a-zA-Z]{4,}", raw.casefold())
    expected = {
        str(item).casefold()
        for item in question.get("typo_terms", [])
        if isinstance(item, str) and len(item) >= 4
    }
    # Valid British/American or documented naming variants should not trigger.
    valid = set(expected)
    for preferred, variants in _VARIANTS.items():
        if preferred in expected or any(v in expected for v in variants):
            valid.add(preferred)
            valid.update(variants)

    warnings: list[str] = []
    for word in answer_words:
        if word in valid:
            continue
        # Avoid warnings on common explanatory words; compare only when the
        # question has explicitly supplied a controlled vocabulary.
        candidates = [
            term for term in valid
            if SequenceMatcher(None, word, term).ratio() >= 0.80
            and word != term
        ]
        if candidates:
            nearest = max(candidates, key=lambda term: SequenceMatcher(None, word, term).ratio())
            warnings.append(
                f"Possible spelling or terminology issue: “{word}” is close to "
                f"“{nearest}”. Check that you used the intended chemistry term."
            )
    normalized = normalize_words(raw)
    for left, right in _DISTINCT_PAIRS:
        if left in expected and right in normalized and left not in normalized:
            warnings.append(
                f"Check the distinction between {left} and {right}; they name different ions or substances."
            )
        elif right in expected and left in normalized and right not in normalized:
            warnings.append(
                f"Check the distinction between {left} and {right}; they name different ions or substances."
            )
    # Stable order and no duplicated notices.
    return list(dict.fromkeys(warnings))


def grade_open_ended(question: dict, response: object) -> dict:
    """Score each authored mark point and return transparent feedback.

    Point match rules supported:
      - match_any: at least one configured phrase/formula appears
      - match_groups: at least one option from every group appears
      - regex_any: at least one configured regular expression matches
      - numeric_targets: at least one number appears within the target tolerance

    If a point defines multiple rule families, every family must pass. This
    permits a numeric point to require both the value and the correct unit.
    """
    raw = str(response or "").strip()
    points = question.get("marking_points", [])
    if not isinstance(points, list):
        points = []
    max_marks = sum(max(0, int(point.get("marks", 1))) for point in points if isinstance(point, dict))
    answer_text = normalize_words(raw)
    compact_text = normalize_notation(raw)
    numbers = _extract_numbers(raw)

    awarded = 0
    point_results = []
    missing = []
    for point in points:
        if not isinstance(point, dict):
            continue
        marks = max(0, int(point.get("marks", 1)))
        matched = bool(raw) and _point_matches(point, raw, answer_text, compact_text, numbers)
        got = marks if matched else 0
        awarded += got
        point_results.append({
            "point_id": point.get("id", ""),
            "criteria": point.get("criteria", ""),
            "marks_awarded": got,
            "marks_available": marks,
            "matched": matched,
        })
        if not matched:
            missing.append(point.get("criteria", "A marking point was not demonstrated."))

    # An authored canonical answer is guaranteed to be a complete model
    # answer. Accept it as full credit even if the individual points use
    # compact matching rules designed for shorter free-form responses.
    canonical_answers = []
    if isinstance(question.get("answer"), str) and question["answer"].strip():
        canonical_answers.append(question["answer"])
    canonical_answers.extend(
        item for item in question.get("accepted_answers", [])
        if isinstance(item, str) and item.strip()
    )
    canonical_hit = any(
        normalize_notation(raw) == normalize_notation(candidate)
        for candidate in canonical_answers
    )
    if canonical_hit and max_marks:
        awarded = max_marks
        for item in point_results:
            item["marks_awarded"] = item["marks_available"]
            item["matched"] = True
        missing = []

    warnings = detect_typo_warnings(raw, question)
    full_credit = bool(max_marks) and awarded == max_marks
    feedback = []
    if not raw:
        feedback.append("Enter a response so it can be marked.")
    elif full_credit:
        feedback.append("All configured marking points were demonstrated.")
    else:
        feedback.append("Some marking points were not demonstrated. Use the feedback below to identify what to review.")
    if missing:
        feedback.extend(f"Review: {item}" for item in missing)
    if not points:
        feedback.append("This question has no marking rubric configured; it has not been assigned a score.")

    return {
        "marks_awarded": awarded,
        "max_marks": max_marks,
        "percent": round(awarded / max_marks * 100) if max_marks else 0,
        "is_full_credit": full_credit,
        "point_results": point_results,
        "missing_points": missing,
        "warnings": warnings,
        "feedback": feedback,
        "raw_response": raw,
        "engine": "deterministic-rubric-1",
    }


__all__ = ["grade_open_ended", "detect_typo_warnings", "normalize_notation", "normalize_words"]
