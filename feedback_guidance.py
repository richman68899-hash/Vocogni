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
    "adding fractions": (
        "Check whether the denominators represent equal-sized parts before adding.",
        "If denominators match, add the numerators and keep the denominator. If they do "
        "not match, make equivalent fractions first.",
    ),
    "subtracting unlike fractions": (
        "Fractions with different denominators describe different-sized parts, so they "
        "cannot be subtracted directly.",
        "Find a common denominator, rewrite both fractions as equivalent fractions, "
        "then subtract the numerators.",
    ),
    "scaling a recipe": (
        "Scaling changes every ingredient by the same factor; adding the same amount "
        "to each ingredient does not scale a recipe.",
        "Multiply each original ingredient amount by the number of batches and keep "
        "the units with the result.",
    ),
    "two-step equations": (
        "Undo the operations in reverse order while keeping both sides of the equation balanced.",
        "Undo addition or subtraction first, then undo multiplication or division; "
        "substitute the result to check.",
    ),
    "equations with brackets": (
        "The bracketed expression is treated as one quantity, and the outside operation "
        "must be undone consistently.",
        "First undo the factor outside the brackets, then solve the remaining equation "
        "and check by substitution.",
    ),
    "budget and break-even reasoning": (
        "Break-even occurs when total revenue equals total cost; fixed and per-item "
        "amounts play different roles.",
        "Write separate expressions for revenue and cost, set them equal, and solve "
        "for the quantity.",
    ),
    "misidentifying the operation": (
        "The operation must represent the relationship between the quantities, not a "
        "keyword in isolation.",
        "Describe what happens to the quantities in a sentence, then choose the operation "
        "that models that relationship.",
    ),
    "forming an equation": (
        "An equation needs two expressions that represent the same quantity or value.",
        "Define the unknown, translate each side of the relationship separately, then "
        "join them with an equals sign.",
    ),
    "sharing a multi-step cost": (
        "A shared total may contain both a fixed amount and a variable amount; combine "
        "them before dividing among people.",
        "Calculate the full cost first, then divide by the number of people and check "
        "that the result is a per-person amount.",
    ),
    "budget-constrained planning": (
        "A plan must satisfy the budget as well as the other conditions in the problem.",
        "Calculate the cost of each option, compare the total with the budget, and "
        "check every stated constraint.",
    ),
    "angles on a straight line": (
        "Angles on a straight line add to 180 degrees.",
        "Add the known angles, subtract their total from 180 degrees, and check that "
        "the result completes the straight line.",
    ),
    "angles around a point": (
        "Angles around a point make one full turn, which is 360 degrees.",
        "Add the known angles and subtract their total from 360 degrees.",
    ),
    "vertically opposite angles": (
        "Vertically opposite angles are equal when two straight lines cross.",
        "Identify the opposite angle pair before using equality; adjacent angles are "
        "not the vertically opposite pair.",
    ),
    "angles in a triangle": (
        "The interior angles of a triangle add to 180 degrees.",
        "Add the known interior angles and subtract from 180 degrees to find the missing angle.",
    ),
    "forming angle equations": (
        "An angle equation must reflect the geometric relationship, such as a straight "
        "line total or equal vertically opposite angles.",
        "Label the relevant angles first, write the relationship in an equation, and "
        "then solve for the unknown.",
    ),
    "clock hand roles": (
        "The long hand shows minutes and the short hand shows hours.",
        "Read the minute hand first, then use the hour hand to identify the current hour.",
    ),
    "counting minute groups of five": (
        "Each number reached by the minute hand represents five-minute groups.",
        "Count by fives from 12 to the minute hand, then add any individual minute marks.",
    ),
    "counting individual minute ticks": (
        "Each small mark between the numbered positions represents one minute.",
        "Count the five-minute groups first, then count the extra individual marks.",
    ),
    "hour hand position": (
        "The hour hand moves gradually; it does not jump to the next number at the half-hour.",
        "Use the number the hour hand has already passed, not the number it is approaching.",
    ),
    "combining hour and minute hands": (
        "The time depends on both hands: one identifies the hour and the other the minutes.",
        "Read the hour the short hand has passed, then read the minute hand in five-minute "
        "groups and individual ticks.",
    ),
    "reading past and to language": (
        "'Past' counts forward from the hour, while 'to' counts the minutes remaining "
        "until the next hour.",
        "For 'past', state the current hour and minutes after it. For 'to', subtract "
        "the stated minutes from the next hour.",
    ),
    "elapsed time across an hour": (
        "Elapsed time across an hour is easier to calculate in two intervals.",
        "Count from the start time to the next exact hour, then add the remaining minutes.",
    ),
    "time in a real schedule": (
        "A schedule question asks for a clock time, so elapsed minutes must be carried "
        "across hour boundaries.",
        "Add the duration in manageable intervals and check whether the result crosses "
        "an hour or day boundary.",
    ),
    "combining both hands": (
        "The hour and minute hands provide different parts of the time and must be read together.",
        "Read the hour already passed, then calculate minutes from the minute hand.",
    ),
    "elapsed time": (
        "Elapsed time is the duration between two clock times, not simply the difference "
        "between the minute numbers.",
        "Count to the next hour first, then add the remaining interval.",
    ),
    "complete analog time reading": (
        "A complete clock reading combines the hour already passed with the minute value.",
        "Read the short hand's current hour, then the long hand's minutes, and combine them.",
    ),
    "minute counting transfer": (
        "A minute-hand position can include both five-minute groups and extra single minutes.",
        "Count the numbered groups by fives, then add the small tick marks.",
    ),
    "hour-hand position transfer": (
        "The hour hand moves continuously between hour numbers.",
        "Use the hour number it has passed, then verify the minute-hand reading.",
    ),
    "past and to language transfer": (
        "The phrase 'to' refers to minutes before the next hour, not minutes after the current hour.",
        "Subtract the stated minutes from the next hour to convert the phrase into digital time.",
    ),
    "elapsed time transfer": (
        "A duration that crosses an hour boundary must include both parts of the interval.",
        "Split the interval at the next exact hour, then add the remaining minutes.",
    ),
    "real-schedule transfer": (
        "A real schedule combines a start time and duration; keep the clock format consistent.",
        "Add the duration in hour-and-minute steps and check the final clock time.",
    ),
}


# Short worked examples provide a second representation, not another diagnosis.
# These are deliberately authored and limited to tags reviewed for this prototype.
_WORKED_EXAMPLES = {
    "denominator confusion": "Example: 3 of 5 equal slices is 3/5. The 5 counts every equal slice; the 3 counts the selected slices.",
    "meaning of the denominator": "Example: In 2/7, the whole is divided into 7 equal parts. The 2 tells how many of those parts are selected.",
    "representing fractions": "Example: If 4 of 6 equal boxes are shaded, write 4/6: shaded boxes on top, all equal boxes on the bottom.",
    "addition error": "Example: 1/5 + 2/5 = 3/5. Each part is the same size, so combine the counts (1 + 2) and keep the denominator 5.",
    "adding fractions": "Example: 1/4 + 2/4 = 3/4. If the denominators match, add only the numerators.",
    "subtracting unlike fractions": "Example: 1/2 - 1/4 = 2/4 - 1/4 = 1/4. First rewrite both fractions with the same denominator.",
    "incorrect simplification": "Example: 6/8 = 3/4 because both 6 and 8 are divided by 2. Dividing only one number would change the value.",
    "incorrect inverse operation": "Example: x + 4 = 9. Subtract 4 from both sides: x = 5. Both sides must stay balanced.",
    "inverse operations": "Example: 3x = 12. Divide both sides by 3, so x = 4. Check: 3 × 4 = 12.",
    "sign errors": "Example: 5 - 8 = -3, not 3. Moving 3 units below zero gives a negative result.",
    "meaning of a variable": "Example: If x is the number of notebooks, then 3x means three times that number, not x + 3.",
    "variable misunderstanding": "Example: If x = 4, then 2x = 2 × 4 = 8. The letter represents a number.",
    "angles on a straight line": "Example: If one angle is 65°, the adjacent angle on the same straight line is 180° - 65° = 115°.",
    "angles around a point": "Example: If three angles around a point are 90°, 120°, and 80°, the fourth is 360° - 290° = 70°.",
    "angles in a triangle": "Example: A triangle with angles 50° and 60° has a third angle of 180° - 110° = 70°.",
    "clock hand roles": "Example: At 3:00, the short hour hand points to 3 and the long minute hand points to 12.",
    "counting minute groups of five": "Example: When the minute hand points to 4, count four groups of five: 5, 10, 15, 20 minutes.",
    "counting individual minute ticks": "Example: If the minute hand is one small tick after the 2, read 11 minutes (10 + 1), not 10.",
    "hour hand position": "Example: At 4:45, the hour hand has passed 4 and is moving toward 5. The current hour is still 4.",
    "reading past and to language": "Example: 20 minutes to 6 means 6:00 - 20 minutes = 5:40.",
    "elapsed time across an hour": "Example: From 2:50 to 3:20 is 10 minutes to 3:00, then 20 more minutes: 30 minutes total.",
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
    return {
        "likely_issue": guidance[0],
        "next_step": guidance[1],
        "worked_example": _WORKED_EXAMPLES.get(key, ""),
        "source_tag": raw_tag,
    }
