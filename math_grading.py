"""Transparent, criterion-level grading for open-ended algebra and graphs practice."""
from __future__ import annotations

import re
from typing import Any

_SUPERSCRIPTS = str.maketrans({
    "⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4",
    "⁵": "^5", "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9",
    "⁺": "+", "⁻": "-",
})
_SUBSCRIPTS = str.maketrans({"₀":"0","₁":"1","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9"})


def normalize_answer(value: Any) -> str:
    """Normalize mathematical typography without deleting operators or changing meaning."""
    text = str(value or "").strip().casefold()
    text = text.translate(_SUPERSCRIPTS).translate(_SUBSCRIPTS)
    for old, new in (("−", "-"), ("–", "-"), ("—", "-"), ("×", "*"), ("·", "*"),
                     ("÷", "/"), ("≤", "<="), ("≥", ">="), ("≠", "!="),
                     ("→", "->"), ("π", "pi"), ("√", "sqrt")):
        text = text.replace(old, new)
    text = re.sub(r"\s+", "", text)
    return text


def _contains(answer: str, phrase: Any) -> bool:
    needle = normalize_answer(phrase)
    return bool(needle) and needle in answer


def _numeric_match(answer: str, targets: list[dict[str, Any]]) -> bool:
    found = []
    # Avoid interpreting the exponent in x^2 as a separate answer number.
    cleaned = re.sub(r"\^[0-9]+", "", answer)
    for raw in re.findall(r"(?<![a-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", cleaned):
        try:
            found.append(float(raw))
        except ValueError:
            continue
    for target in targets:
        expected = float(target["value"])
        tolerance = float(target.get("tolerance", max(abs(expected) * 1e-4, 1e-9)))
        if not any(abs(value - expected) <= tolerance for value in found):
            return False
    return bool(targets)


def _point_awarded(point: dict[str, Any], answer: str) -> bool:
    checks = []
    if point.get("match_all"):
        checks.append(all(_contains(answer, term) for term in point["match_all"]))
    if point.get("match_any"):
        checks.append(any(_contains(answer, term) for term in point["match_any"]))
    if point.get("match_groups"):
        checks.append(all(any(_contains(answer, term) for term in group)
                          for group in point["match_groups"]))
    if point.get("regex_any"):
        checks.append(any(re.search(pattern, answer, re.IGNORECASE)
                          for pattern in point["regex_any"]))
    if point.get("numeric_targets"):
        checks.append(_numeric_match(answer, point["numeric_targets"]))
    return bool(checks) and all(checks)


def evaluate_open_response(question: dict[str, Any], answer: Any) -> dict[str, Any]:
    """Return reproducible rubric marks and the evidence for each criterion."""
    raw = str(answer or "").strip()
    normalized = normalize_answer(raw)
    points = question.get("marking_points", [])
    maximum = int(question.get("max_marks", sum(int(p.get("marks", 1)) for p in points)))
    accepted = [normalize_answer(item) for item in
                list(question.get("accepted_answers", [])) + [question.get("answer", "")]]
    exact_match = bool(normalized and normalized in accepted)

    results = []
    awarded = 0
    for index, point in enumerate(points, start=1):
        available = int(point.get("marks", 1))
        met = exact_match or _point_awarded(point, normalized)
        earned = available if met else 0
        awarded += earned
        results.append({
            "id": point.get("id", f"point_{index}"),
            "criteria": point.get("criteria", "Marking point"),
            "marks_awarded": earned,
            "marks_available": available,
            "feedback": point.get("feedback", ""),
            "met": earned == available,
        })
    awarded = min(awarded, maximum)
    missed = [item for item in results if not item["met"]]
    return {
        "score": awarded,
        "max_marks": maximum,
        "percent": round(awarded / maximum * 100) if maximum else 0,
        "full_credit": maximum > 0 and awarded == maximum,
        "exact_answer_match": exact_match,
        "marking_points": results,
        "missed_points": missed,
        "feedback": (f"Full marks: {awarded}/{maximum}." if awarded == maximum
                     else f"{awarded}/{maximum} marks. Review the unmet criteria."),
        "typo_warning": None,
        "normalized_answer": normalized,
    }


def validate_open_response_question(question: dict[str, Any]) -> list[str]:
    errors = []
    if question.get("type") != "open_ended":
        return errors
    maximum = question.get("max_marks")
    points = question.get("marking_points")
    if not isinstance(maximum, int) or maximum < 1:
        errors.append("open_ended question needs a positive integer max_marks")
    if not isinstance(points, list) or not points:
        errors.append("open_ended question needs at least one marking_points item")
        return errors
    for index, point in enumerate(points, start=1):
        if not isinstance(point, dict) or int(point.get("marks", 0)) < 1:
            errors.append(f"marking point {index} needs positive integer marks")
            continue
        if not any(point.get(key) for key in ("match_all", "match_any", "match_groups", "regex_any", "numeric_targets")):
            errors.append(f"marking point {index} has no matching rule")
    if all(isinstance(p, dict) and int(p.get("marks", 0)) > 0 for p in points):
        if sum(int(p["marks"]) for p in points) != int(maximum or 0):
            errors.append("marking-point total must equal max_marks exactly")
    return errors
