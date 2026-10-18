"""Rubric-based open-response grading for Vocogni chemistry lessons.

This module is deterministic and auditable. It is a practice grader, not an
official Cambridge mark scheme or an examiner-equivalent system.
"""
from __future__ import annotations

import difflib
import re
from typing import Any

_SUBSCRIPT = str.maketrans({
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
})
_SUPERSCRIPT = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁺": "+", "⁻": "-",
})


def normalize_answer(value: Any) -> str:
    """Normalise typing and notation without equating different chemistry."""
    text = str(value or "").strip().casefold()
    text = text.translate(_SUBSCRIPT).translate(_SUPERSCRIPT)
    text = (text.replace("→", "->").replace("⟶", "->")
                .replace("⟹", "->").replace("⇒", "->")
                .replace("−", "-").replace("–", "-").replace("—", "-"))
    # Accept common spelling/typography variants, not chemically different ions.
    text = text.replace("sulphate", "sulfate").replace("sulphite", "sulfite")
    text = text.replace("aluminum", "aluminium")
    text = re.sub(r"\s+", "", text)
    return text


def _contains(answer: str, phrase: Any) -> bool:
    needle = normalize_answer(phrase)
    return bool(needle) and needle in answer


def _numeric_match(answer: str, targets: list[dict[str, Any]]) -> bool:
    found = []
    for raw in re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", answer):
        try:
            found.append(float(raw))
        except ValueError:
            pass
    for target in targets:
        expected = float(target["value"])
        tolerance = float(target.get("tolerance", max(abs(expected) * 1e-4, 1e-9)))
        if not any(abs(value - expected) <= tolerance for value in found):
            return False
    return bool(targets)


def _point_awarded(point: dict[str, Any], normalized: str) -> bool:
    checks_present = False
    passed = True

    all_terms = point.get("match_all", [])
    if all_terms:
        checks_present = True
        passed = passed and all(_contains(normalized, term) for term in all_terms)

    any_terms = point.get("match_any", [])
    if any_terms:
        checks_present = True
        passed = passed and any(_contains(normalized, term) for term in any_terms)

    groups = point.get("match_groups", [])
    if groups:
        checks_present = True
        passed = passed and all(
            any(_contains(normalized, term) for term in group)
            for group in groups
        )

    patterns = point.get("regex_any", [])
    if patterns:
        checks_present = True
        passed = passed and any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns)

    targets = point.get("numeric_targets", [])
    if targets:
        checks_present = True
        passed = passed and _numeric_match(normalized, targets)

    return bool(checks_present and passed)


def detect_typo_warning(answer: Any, question: dict[str, Any]) -> str | None:
    """Flag probable spelling confusion; never silently autocorrect a response."""
    raw = str(answer or "")
    terms = question.get("typo_terms", [])
    if not raw.strip() or not terms:
        return None
    known = {normalize_answer(term) for term in terms}
    words = re.findall(r"[A-Za-z]{5,}", raw.casefold())
    for word in words:
        norm_word = normalize_answer(word)
        if norm_word in known:
            continue
        match = difflib.get_close_matches(norm_word, list(known), n=1, cutoff=0.68)
        if match:
            intended = next((str(term) for term in terms if normalize_answer(term) == match[0]), match[0])
            return (
                f"Possible terminology typo: “{word}” resembles “{intended}”. "
                "Check whether you meant that term or a different chemical species. "
                "Your answer has not been changed."
            )
    return None


def evaluate_open_response(question: dict[str, Any], answer: Any) -> dict[str, Any]:
    """Return awarded marks, criterion-level evidence, feedback, and typo warning."""
    text = str(answer or "").strip()
    points = question.get("marking_points", [])
    declared_max = int(question.get("max_marks", sum(int(p.get("marks", 1)) for p in points)))
    # The configured model answer is a known-complete reference response.
    # Exact matching is only one route to full credit; other responses still
    # earn criterion-level marks through the rubric below.
    accepted = [
        normalize_answer(item)
        for item in list(question.get("accepted_answers", [])) + [question.get("answer", "")]
    ]
    normalized = normalize_answer(text)
    exact_match = bool(normalized and normalized in accepted)

    point_results = []
    awarded = 0
    for index, point in enumerate(points, start=1):
        marks = max(0, int(point.get("marks", 1)))
        earned = marks if (exact_match or _point_awarded(point, normalized)) else 0
        awarded += earned
        point_results.append({
            "id": point.get("id", f"point_{index}"),
            "criteria": point.get("criteria", "Marking point"),
            "marks_awarded": earned,
            "marks_available": marks,
            "feedback": point.get("feedback", ""),
            "met": earned == marks,
        })

    if exact_match and not points:
        awarded = declared_max

    awarded = min(awarded, declared_max)
    warning = detect_typo_warning(text, question)
    missed = [item for item in point_results if not item["met"]]
    feedback = (
        f"Full marks: {awarded}/{declared_max}."
        if awarded == declared_max
        else f"{awarded}/{declared_max} marks. Review the unmet marking points below."
    )
    return {
        "score": awarded,
        "max_marks": declared_max,
        "percent": round(100 * awarded / declared_max) if declared_max else 0,
        "full_credit": declared_max > 0 and awarded == declared_max,
        "exact_answer_match": exact_match,
        "marking_points": point_results,
        "missed_points": missed,
        "feedback": feedback,
        "typo_warning": warning,
        "normalized_answer": normalized,
    }


def validate_open_response_question(question: dict[str, Any]) -> list[str]:
    """Validate a course author's open-response rubric before it reaches learners."""
    errors = []
    if question.get("type") != "open_ended":
        return errors
    max_marks = question.get("max_marks")
    points = question.get("marking_points")
    if not isinstance(max_marks, int) or max_marks < 1:
        errors.append("open_ended question needs a positive integer max_marks")
    if not isinstance(points, list) or not points:
        errors.append("open_ended question needs at least one marking_points item")
        return errors
    if any(not isinstance(point, dict) or int(point.get("marks", 0)) < 1 for point in points):
        errors.append("each marking point needs positive integer marks")
    elif sum(int(point.get("marks", 0)) for point in points) != int(max_marks or 0):
        errors.append("marking-point total must equal max_marks exactly")
    for index, point in enumerate(points, start=1):
        if not any(point.get(key) for key in ("match_all", "match_any", "match_groups", "regex_any", "numeric_targets")):
            errors.append(f"marking point {index} has no matching rule")
    return errors
