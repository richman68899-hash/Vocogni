"""Deterministic, authored guidance for common mathematics errors.

Guidance is attached to an authored mistake tag. It describes a likely issue
to check, not a diagnosis of the learner's thinking. Unknown tags receive no
invented misconception label.
"""
from __future__ import annotations

from typing import Any


_GUIDANCE = {
    "denominator confusion": (
        "Check what the denominator represents: the number of equal parts in the whole, "
        "not the number of parts selected.",
        "Draw or imagine the whole split into equal parts, label the total parts first, "
        "then count the selected parts.",
    ),
    "meaning of the denominator": (
        "The denominator describes how many equal parts make one whole.",
        "Before writing the fraction, state the total number of equal parts and then "
        "count how many are being discussed.",
    ),
    "representing fractions": (
        "Check that the numerator counts the selected parts and the denominator counts "
        "all equal parts in the whole.",
        "Represent the situation with a labelled bar or set, then write the fraction.",
    ),
    "addition error": (
        "For fractions with the same denominator, the denominator stays the same; "
        "the numerators are added.",
        "Rewrite the addition as equal-sized parts, add only the numerator values, "
        "and simplify only after the addition.",
    ),
    "incorrect simplification": (
        "A fraction is simplified by dividing the numerator and denominator by the "
        "same common factor.",
        "Find a common factor of both numbers, divide both by it, and check that the "
        "fraction's value has not changed.",
    ),
    "incorrect inverse operation": (
        "An equation stays balanced only when the same operation is applied to both sides.",
        "Identify the operation applied to the unknown, then undo it on both sides "
        "before calculating.",
    ),
    "inverse operations": (
        "Use the operation that reverses the operation attached to the unknown.",
        "Undo addition or subtraction first, then multiplication or division as needed; "
        "check by substituting your result.",
    ),
    "sign errors": (
        "A negative sign changes the value and must be carried through each operation.",
        "Write each operation on a new line and check the sign before simplifying.",
    ),
    "meaning of a variable": (
        "A variable is a symbol representing a number; its value depends on the situation "
        "or equation.",
        "Read the sentence and identify what quantity the letter represents before "
        "choosing an expression.",
    ),
    "variable misunderstanding": (
        "A variable stands for a number; it is not itself an operation or a fixed answer.",
        "Replace the letter with a simple test value and check whether the expression "
        "matches the situation.",
    ),
    "translating key words": (
        "A keyword can suggest an operation, but the relationship in the full sentence "
        "determines the correct expression.",
        "Name the quantities, describe how they relate in plain language, and only then "
        "write the operation.",
    ),
    "choosing a basic operation": (
        "The operation should match what the question asks you to find, not just one "
        "isolated word.",
        "Ask whether the situation combines, compares, groups, or shares quantities "
        "before selecting an operation.",
    ),
    "selecting relevant information": (
        "Not every number in a word problem is necessarily needed for the requested result.",
        "Underline the target quantity and keep only the information that helps calculate it.",
    ),
    "building a cost model": (
        "Separate fixed costs from costs that change with each item before forming an equation.",
        "Write total cost as fixed cost plus (cost per item × number of items), then check "
        "the units.",
    ),
    "application / transfer error": (
        "The mathematical idea may be familiar, but the real-world situation changes how "
        "the quantities are represented.",
        "List the known quantities with units, identify the unknown, and map each one "
        "to the relevant mathematical operation.",
    ),
}


def build_feedback_guidance(question: dict[str, Any]) -> dict[str, str] | None:
    """Return carefully scoped guidance for a recognised authored mistake tag."""
    if not isinstance(question, dict):
        return None
    raw_tag = question.get("mistake_tag")
    if not isinstance(raw_tag, str) or not raw_tag.strip():
        return None
    key = " ".join(raw_tag.strip().casefold().split())
    guidance = _GUIDANCE.get(key)
    if guidance is None:
        return None
    return {"likely_issue": guidance[0], "next_step": guidance[1], "source_tag": raw_tag}
