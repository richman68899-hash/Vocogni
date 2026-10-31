"""Explainable, heuristic recognition of recurring learning-error patterns.

This is a transparent prototype, not a trained model or validated diagnosis.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

PATTERNS: dict[str, dict[str, str]] = {
    "sign_error": {
        "label": "Sign handling",
        "description": "A sign may have changed incorrectly during a calculation.",
        "review": "Track each positive/negative sign on a separate line and substitute the result to check it.",
    },
    "inverse_operation": {
        "label": "Inverse operations",
        "description": "An operation may not have been undone correctly when isolating a variable.",
        "review": "Apply the inverse operation to both sides, preserving equality.",
    },
    "equality_balance": {
        "label": "Maintaining equality",
        "description": "A transformation may have been applied to only one side of an equation.",
        "review": "Write the same operation on both sides before simplifying.",
    },
    "fraction_denominator": {
        "label": "Fraction denominators",
        "description": "Numerators or denominators may have been combined using an invalid rule.",
        "review": "Find a common denominator before adding or subtracting fractions.",
    },
    "distribution": {
        "label": "Distributive property",
        "description": "A factor may not have been applied to every term inside parentheses.",
        "review": "Multiply the outside factor by each term, including its sign.",
    },
    "keyword_matching": {
        "label": "Keyword-based reasoning",
        "description": "The solution may rely on a familiar word instead of the relationships in the problem.",
        "review": "Represent the quantities and their relationships before choosing an operation.",
    },
}

_RULES: dict[str, tuple[str, ...]] = {
    "sign_error": (r"\b(sign error|forgot the minus|negative became positive|positive became negative|wrong sign)\b|changed\s+-?\d+\s+to\s+\+?\d+",),
    "inverse_operation": (r"\b(inverse operation|divided instead of multiplied|added instead of subtract|subtract instead of add|isolat(?:e|ing) the variable)\b",),
    "equality_balance": (r"\b(one side|both sides|balance the equation|only on the left|only on the right)\b",),
    "fraction_denominator": (r"\b(add(?:ed|ing)? denominators|subtract(?:ed|ing)? denominators|common denominator|fraction denominator)\b",),
    "distribution": (r"\b(distribut(?:e|ed|ive)|expand(?:ed|ing)?|forgot to multiply|outside factor)\b",),
    "keyword_matching": (r"\b(keyword|key word|saw the word|word meant|automatically chose|without modelling)\b",),
}


def detect_patterns(text: str) -> list[dict[str, str]]:
    """Return pattern candidates explicitly signalled by the supplied text."""
    normalized = str(text or "").casefold()
    found = []
    for key, expressions in _RULES.items():
        if any(re.search(expression, normalized) for expression in expressions):
            found.append({"key": key, **PATTERNS[key]})
    return found


def analyze_attempts(attempts: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Aggregate only explicitly signalled patterns in incorrect attempts."""
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = {}
    inspected = 0
    for attempt in attempts or []:
        if not isinstance(attempt, dict) or attempt.get("correct") is not False:
            continue
        inspected += 1
        evidence = " ".join(str(attempt.get(field, "")) for field in ("question", "response", "feedback", "mistake_tag"))
        for match in detect_patterns(evidence):
            counts[match["key"]] += 1
            examples.setdefault(match["key"], [])
            if len(examples[match["key"]]) < 2:
                examples[match["key"]].append(str(attempt.get("question") or attempt.get("response") or "Recorded incorrect attempt")[:180])
    results = []
    for key, count in counts.most_common():
        item = {"key": key, **PATTERNS[key], "evidence_count": count, "examples": examples[key]}
        item["signal"] = "repeated signal" if count >= 3 else "early signal"
        results.append(item)
    return {
        "incorrect_attempts_inspected": inspected,
        "patterns": results,
        "interpretation": "Heuristic signals from the text supplied; not proof of a stable misconception or a measure of ability.",
    }
