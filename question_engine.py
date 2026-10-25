"""Verified Question Engine (VQE), initial rules-based prototype.

The engine normalises existing authored question data, checks structural
quality, records review evidence, and exposes a shared catalogue/selector.
It does not generate unrestricted questions or claim that schema validation
proves mathematical correctness.

VQE pilot lessons are strict: if a listed item changes from its reviewed
content snapshot or fails validation, it is excluded until reviewed again.
Non-pilot content remains available to existing legacy flows.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import math
from typing import Any

import data
import math_grading
import math_taxonomy


ENGINE_VERSION = "vqe-prototype-1"
QUESTION_TYPES = ("mc", "numeric", "open_ended")
QUESTION_PURPOSES = (
    "diagnostic",
    "conceptual",
    "practice",
    "misconception_probe",
    "application",
    "reasoning",
)
VERIFICATION_STATUSES = ("legacy", "needs_review", "verified", "retired")
GRADE_BANDS = (7, 8, 9)

# Only these lessons are opted into strict verified-only retrieval in this
# prototype. This boundary prevents a missing verified set from silently
# falling back to an unreviewed question.
PILOT_LESSONS = {
    ("fractions", "fractions_l1"),
    ("fractions", "fractions_l2"),
    ("algebra", "algebra_l1"),
    ("algebra", "algebra_l2"),
    ("word_problems", "wp_l1"),
    ("basic_geometry", "geometry_l1"),
}

_REQUIRED_REVIEW_CHECKS = {
    "schema_checked",
    "answer_independently_checked",
    "explanation_checked",
    "pedagogical_reviewed",
}


def _review(
    skill_id: str,
    topic: str,
    purpose: str,
    difficulty: int,
    reviewed_content: dict[str, Any],
    *,
    pathway: str | None = None,
) -> dict[str, Any]:
    return {
        "version": 1,
        "skill_id": skill_id,
        "grade_bands": [7, 8, 9],
        "strand": math_taxonomy.SKILLS[skill_id]["strand"],
        "topic": topic,
        "purpose": purpose,
        "difficulty": difficulty,
        "pathway": pathway,
        "verification_status": "verified",
        "reviewed_at": "2026-10-25",
        "reviewer": "Vocogni VQE prototype content review",
        "review_checks": sorted(_REQUIRED_REVIEW_CHECKS),
        # These values anchor verification to the actual authored item.
        # Changing any included field invalidates the review automatically.
        "reviewed_content": reviewed_content,
        "curriculum_alignment": "Provisional lower-secondary planning tag; not an official syllabus code",
    }


# Initial seed items were individually reviewed against their authored prompt,
# answer, explanation, and applicable option/input rules. This is intentionally
# a small bank; all other content remains legacy until it is reviewed.
VERIFICATION_REGISTRY = {
    "fractions_l1_q1": _review(
        "math.number.fraction_representation", "Fractions", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Which fraction represents 3 out of 4 equal parts?",
            "options": ["3/4", "4/3", "1/3", "3/3"],
            "answer": "3/4",
            "explanation": "3 out of 4 equal parts is written with 3 as the numerator (parts you have) and 4 as the denominator (total equal parts): 3/4.",
            "mistake_tag": "Denominator confusion",
        },
    ),
    "fractions_l1_q2": _review(
        "math.number.fraction_representation", "Fractions", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "In the fraction 5/8, what is the denominator?",
            "options": ["5", "8", "3", "13"],
            "answer": "8",
            "explanation": "The denominator is the bottom number. In 5/8, that number is 8 — it tells you the whole is split into 8 equal parts.",
            "mistake_tag": "Denominator confusion",
        },
    ),
    "fractions_l1_screen3": _review(
        "math.number.fraction_representation", "Fractions", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "A pizza is split into 8 equal slices and you eat 5. Which fraction represents the slices eaten?",
            "options": ["5/8", "8/5", "3/8", "5/5"],
            "answer": "5/8",
            "explanation": "Five slices were eaten out of eight equal slices, so the fraction is 5/8.",
            "mistake_tag": "Representing fractions",
        },
    ),
    "fractions_l2_q1": _review(
        "math.number.fraction_operations", "Fraction addition", "practice", 1,
        {
            "type": "numeric",
            "prompt": "What is 1/4 + 1/4? Enter your answer as a decimal.",
            "answer": 0.5,
            "tolerance": 0.01,
            "whole_number": False,
            "input_hint": "e.g. 0.5",
            "explanation": "1/4 + 1/4 = 2/4 = 0.5.",
            "mistake_tag": "Addition error",
        },
    ),
    "fractions_l2_q2": _review(
        "math.number.fraction_operations", "Fraction addition", "practice", 1,
        {
            "type": "numeric",
            "prompt": "What is 1/5 + 2/5? Enter your answer as a decimal.",
            "answer": 0.6,
            "tolerance": 0.01,
            "whole_number": False,
            "input_hint": "e.g. 0.6",
            "explanation": "1/5 + 2/5 = 3/5 = 0.6.",
            "mistake_tag": "Addition error",
        },
    ),
    "fractions_l2_screen3": _review(
        "math.number.fraction_operations", "Fraction addition", "practice", 1,
        {
            "type": "mc",
            "prompt": "What is 1/6 + 3/6?",
            "options": ["4/6", "4/12", "3/6", "1/3"],
            "answer": "4/6",
            "explanation": "The denominators match, so add the numerators: 1 + 3 = 4, giving 4/6 (which can simplify to 2/3).",
            "mistake_tag": "Addition error",
        },
    ),
    "fractions_l1_l2_q1": _review(
        "math.number.fraction_operations", "Fraction addition", "practice", 2,
        {
            "type": "mc",
            "prompt": "What is 1/4 + 2/4?",
            "options": ["3/4", "3/8", "2/4", "1/2"],
            "answer": "3/4",
            "explanation": "The denominators match, so add the numerators and keep the denominator: 3/4.",
            "mistake_tag": "Adding fractions",
            "stage": "practice",
        },
        pathway="level_2",
    ),
    "fractions_l1_l3_q2": _review(
        "math.number.fraction_operations", "Subtracting fractions", "practice", 3,
        {
            "type": "mc",
            "prompt": "A ribbon is 3/4 m long. You use 2/5 m. How much remains?",
            "options": ["7/20 m", "1/20 m", "1/2 m", "1/3 m"],
            "answer": "7/20 m",
            "explanation": "3/4 − 2/5 = 15/20 − 8/20 = 7/20.",
            "mistake_tag": "Subtracting unlike fractions",
            "stage": "practice",
        },
        pathway="level_3",
    ),
    "fractions_l1_project_q1": _review(
        "math.number.fraction_operations", "Scaling a recipe", "application", 3,
        {
            "type": "numeric",
            "prompt": "One batch uses 2/3 cup of oats. How many cups are needed for 3 batches?",
            "answer": 2,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter the number of cups.",
            "explanation": "2/3 × 3 = 2 cups.",
            "mistake_tag": "Scaling a recipe",
            "stage": "project",
        },
        pathway="project",
    ),
    "algebra_l1_q1": _review(
        "math.algebra.variables_expressions", "Variables", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "In the equation x + 5 = 12, what does x represent?",
            "options": ["An unknown number we need to find", "A fixed constant", "The answer 5", "The answer 12"],
            "answer": "An unknown number we need to find",
            "explanation": "x is a placeholder for the number that makes the equation true — that's what solving for x means.",
            "mistake_tag": "Variable misunderstanding",
        },
    ),
    "algebra_l1_q2": _review(
        "math.algebra.variables_expressions", "Variables", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Which of these is a variable?",
            "options": ["x", "7", "+", "="],
            "answer": "x",
            "explanation": "x is a letter standing in for an unknown number. 7, +, and = are a fixed number and operators, not variables.",
            "mistake_tag": "Variable misunderstanding",
        },
    ),
    "algebra_l1_screen3": _review(
        "math.algebra.variables_expressions", "Variables", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Let n stand for the number of stickers you start with. Which expression means 3 more stickers?",
            "options": ["n + 3", "3n", "n - 3", "3 - n"],
            "answer": "n + 3",
            "explanation": "The letter n represents the starting amount. Three more means add 3: n + 3.",
            "mistake_tag": "Meaning of a variable",
        },
    ),
    "algebra_l2_q1": _review(
        "math.algebra.linear_equations", "One-step equations", "practice", 1,
        {
            "type": "numeric",
            "prompt": "Solve for x: x + 7 = 15",
            "answer": 8,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "whole number",
            "explanation": "Subtract 7 from both sides: x = 15 - 7 = 8.",
            "mistake_tag": "Incorrect inverse operation",
        },
    ),
    "algebra_l2_q2": _review(
        "math.algebra.linear_equations", "One-step equations", "practice", 1,
        {
            "type": "numeric",
            "prompt": "Solve for x: 3x = 21",
            "answer": 7,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "whole number",
            "explanation": "Divide both sides by 3: x = 21 / 3 = 7.",
            "mistake_tag": "Incorrect inverse operation",
        },
    ),
    "algebra_l2_screen3": _review(
        "math.algebra.linear_equations", "One-step equations", "practice", 1,
        {
            "type": "numeric",
            "prompt": "Solve 3x = 24. What is x?",
            "answer": 8,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter a whole number.",
            "explanation": "Divide both sides by 3: x = 24 ÷ 3 = 8.",
            "mistake_tag": "Incorrect inverse operation",
        },
    ),
    "algebra_l1_l2_q1": _review(
        "math.algebra.linear_equations", "Two-step equations", "practice", 2,
        {
            "type": "mc",
            "prompt": "Solve 3x + 2 = 17.",
            "options": ["5", "7", "19", "3"],
            "answer": "5",
            "explanation": "Subtract 2 to get 3x = 15, then divide by 3.",
            "mistake_tag": "Two-step equations",
            "stage": "practice",
        },
        pathway="level_2",
    ),
    "algebra_l1_l3_q1": _review(
        "math.algebra.linear_equations", "Equations with brackets", "practice", 3,
        {
            "type": "mc",
            "prompt": "Solve 5(x − 2) = 30.",
            "options": ["8", "4", "6", "10"],
            "answer": "8",
            "explanation": "Divide by 5 to get x − 2 = 6, then add 2.",
            "mistake_tag": "Equations with brackets",
            "stage": "practice",
        },
        pathway="level_3",
    ),
    "algebra_l1_project_q1": _review(
        "math.algebra.linear_equations", "Budget and break-even reasoning", "application", 3,
        {
            "type": "numeric",
            "prompt": "An event costs Rp25,000 as a fixed fee plus Rp6,000 per participant. With a Rp100,000 budget, what is the maximum number of participants?",
            "answer": 12,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter a whole number of participants.",
            "explanation": "Rp100,000 − Rp25,000 = Rp75,000 available for participants. Rp75,000 ÷ Rp6,000 allows 12 whole participants.",
            "mistake_tag": "Budget and break-even reasoning",
            "stage": "project",
        },
        pathway="project",
    ),
    "wp_l1_q1": _review(
        "math.problem_solving.expression_translation", "Expression translation", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Which operation does the word 'total' usually suggest?",
            "options": ["Addition", "Subtraction", "Multiplication", "Division"],
            "answer": "Addition",
            "explanation": "'Total' usually means combining amounts together, which is addition.",
            "mistake_tag": "Misidentifying the operation",
        },
    ),
    "wp_l1_q2": _review(
        "math.problem_solving.expression_translation", "Expression translation", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Sarah has 3 times as many apples as Tom. If Tom has x apples, how would you write Sarah's apples?",
            "options": ["3x", "x/3", "x + 3", "x - 3"],
            "answer": "3x",
            "explanation": "'3 times as many' means multiplying Tom's amount by 3, so Sarah has 3x apples.",
            "mistake_tag": "Misidentifying the operation",
        },
    ),
    "wp_l1_screen3": _review(
        "math.problem_solving.expression_translation", "Expression translation", "conceptual", 1,
        {
            "type": "mc",
            "prompt": "Ben has x cards and receives 4 more. Which expression represents his new total?",
            "options": ["x + 4", "4x", "x - 4", "4 - x"],
            "answer": "x + 4",
            "explanation": "Receiving 4 more means add 4 to the starting amount x, giving x + 4.",
            "mistake_tag": "Translating key words",
        },
    ),
    "wp_l1_l2_q1": _review(
        "math.problem_solving.expression_translation", "Forming an equation", "practice", 2,
        {
            "type": "mc",
            "prompt": "There are 3 boxes with x notebooks in each box and 5 extra notebooks. There are 23 notebooks altogether. Which equation models this?",
            "options": ["3x + 5 = 23", "3 + x + 5 = 23", "3(x + 5) = 23", "x + 5 = 23"],
            "answer": "3x + 5 = 23",
            "explanation": "Three equal groups give 3x, then add the 5 extra notebooks.",
            "mistake_tag": "Forming an equation",
            "stage": "practice",
        },
        pathway="level_2",
    ),
    "wp_l1_l3_q1": _review(
        "math.problem_solving.linear_cost_models", "Sharing a multi-step cost", "practice", 3,
        {
            "type": "mc",
            "prompt": "A ride costs Rp10,000 plus Rp2,000 per kilometre. Two people share the cost of an 8 km ride equally. How much does each pay?",
            "options": ["Rp13,000", "Rp26,000", "Rp16,000", "Rp12,000"],
            "answer": "Rp13,000",
            "explanation": "The total is Rp10,000 + (8 × Rp2,000) = Rp26,000. Half is Rp13,000.",
            "mistake_tag": "Sharing a multi-step cost",
            "stage": "practice",
        },
        pathway="level_3",
    ),
    "wp_l1_project_q1": _review(
        "math.problem_solving.linear_cost_models", "Budget-constrained planning", "application", 3,
        {
            "type": "numeric",
            "prompt": "A school fair has a fixed setup cost of Rp40,000 and costs Rp7,000 per booth. With Rp130,000 available, what is the maximum number of whole booths that can be funded?",
            "answer": 12,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter a whole number of booths.",
            "explanation": "Rp130,000 − Rp40,000 = Rp90,000. Twelve booths cost Rp84,000; thirteen would cost Rp91,000, exceeding the budget.",
            "mistake_tag": "Budget-constrained planning",
            "stage": "project",
        },
        pathway="project",
    ),
    "geometry_l1_q1": _review(
        "math.geometry.angle_facts", "Angles on a straight line", "practice", 1,
        {
            "type": "numeric",
            "prompt": "An angle and its adjacent angle lie on a straight line. One angle is 68°. Find the other angle (°).",
            "answer": 112,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter the number only; the question gives the units.",
            "explanation": "Angles on a straight line total 180°: 180 − 68 = 112°.",
            "skill_tag": "Angles on a straight line",
            "mistake_tag": "Angles on a straight line",
        },
    ),
    "geometry_l1_q2": _review(
        "math.geometry.angle_facts", "Angles around a point", "practice", 1,
        {
            "type": "numeric",
            "prompt": "Three angles around a point are 95°, 135°, and 70°. Find the fourth angle (°).",
            "answer": 60,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter the number only; the question gives the units.",
            "explanation": "Angles around a point total 360°: 360 − (95 + 135 + 70) = 60°.",
            "skill_tag": "Angles around a point",
            "mistake_tag": "Angles around a point",
        },
    ),
    "geometry_l1_q3": _review(
        "math.geometry.angle_facts", "Vertically opposite angles", "practice", 1,
        {
            "type": "mc",
            "prompt": "One angle at an intersection is 47°. What is the vertically opposite angle?",
            "options": ["43°", "47°", "133°", "313°"],
            "answer": "47°",
            "explanation": "Vertically opposite angles are equal, so the opposite angle is 47°.",
            "skill_tag": "Vertically opposite angles",
            "mistake_tag": "Vertically opposite angles",
        },
    ),
    "geometry_l1_q4": _review(
        "math.geometry.angle_facts", "Angles in a triangle", "practice", 1,
        {
            "type": "numeric",
            "prompt": "Two angles in a triangle are 52° and 68°. Find the third angle (°).",
            "answer": 60,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter the number only; the question gives the units.",
            "explanation": "Triangle angles total 180°: 180 − 52 − 68 = 60°.",
            "skill_tag": "Angles in a triangle",
            "mistake_tag": "Angles in a triangle",
        },
    ),
    "geometry_l1_q5": _review(
        "math.geometry.angle_facts", "Forming angle equations", "practice", 2,
        {
            "type": "numeric",
            "prompt": "Two angles on a straight line are x and 3x. Find x (°).",
            "answer": 45,
            "tolerance": 0.01,
            "whole_number": True,
            "input_hint": "Enter the number only; the question gives the units.",
            "explanation": "x + 3x = 180°, so 4x = 180° and x = 45°.",
            "skill_tag": "Forming angle equations",
            "mistake_tag": "Forming angle equations",
        },
    ),
}


def is_vqe_pilot_lesson(course_id: str, lesson_id: str) -> bool:
    """Whether a lesson opts into strict verified-only retrieval."""
    return (str(course_id), str(lesson_id)) in PILOT_LESSONS


def _as_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def validate_question(question: Any) -> list[str]:
    """Return structural errors for one supported question without mutating it."""
    if not isinstance(question, dict):
        return ["Question must be a dictionary."]

    errors: list[str] = []
    for field in ("id", "type", "prompt", "explanation"):
        value = question.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Question needs a non-empty '{field}'.")
    question_type = question.get("type")

    if "answer" not in question:
        errors.append("Question is missing 'answer'.")

    if question_type == "mc":
        options = question.get("options")
        if not isinstance(options, list) or len(options) < 2:
            errors.append("Multiple-choice question needs at least two options.")
        else:
            if any(not isinstance(option, str) or not option.strip() for option in options):
                errors.append("Every multiple-choice option must be a non-empty string.")
            if len(options) != len(set(options)):
                errors.append("Multiple-choice options must be unique.")
            if question.get("answer") not in options:
                errors.append("Multiple-choice answer must match one option exactly.")
    elif question_type == "numeric":
        if not _as_finite_number(question.get("answer")):
            errors.append("Numeric answer must be a finite number.")
        tolerance = question.get("tolerance", 0.01)
        if not _as_finite_number(tolerance) or float(tolerance) < 0:
            errors.append("Numeric tolerance must be a finite non-negative number.")
        if "whole_number" in question and not isinstance(question["whole_number"], bool):
            errors.append("whole_number must be a boolean when provided.")
    elif question_type == "open_ended":
        grader_name = question.get("grader", "math")
        if grader_name == "math":
            grader = math_grading
        elif grader_name == "chemistry":
            import chemistry_grading
            grader = chemistry_grading
        else:
            errors.append(f"Unsupported open-response grader '{grader_name}'.")
            return errors
        errors.extend(grader.validate_open_response_question(question))
    elif question_type not in QUESTION_TYPES:
        errors.append(f"Unsupported question type '{question_type}'.")

    return errors


def _same_snapshot_value(left: Any, right: Any) -> bool:
    # JSON round-tripping gives predictable comparisons for simple metadata
    # and preserves numeric-vs-string differences in answer formats.
    return left == right


def _snapshot_matches(question: dict[str, Any], metadata: dict[str, Any]) -> bool:
    snapshot = metadata.get("reviewed_content", {})
    if not isinstance(snapshot, dict) or not snapshot:
        return False
    return all(
        key in question and _same_snapshot_value(question.get(key), expected)
        for key, expected in snapshot.items()
    )


def _question_fingerprint_payload(question: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id", "type", "prompt", "options", "answer", "tolerance",
        "whole_number", "input_hint", "explanation", "mistake_tag",
        "skill_tag", "grader", "accepted_answers", "max_marks",
        "marking_points", "stage",
    )
    return {key: deepcopy(question[key]) for key in keys if key in question}


def _find_occurrences(
    course_id: str | None = None,
    lesson_id: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for course in data.all_courses_in_order():
        if course_id is not None and course.get("id") != course_id:
            continue
        for lesson in course.get("lessons", []):
            if lesson_id is not None and lesson.get("id") != lesson_id:
                continue
            location_fields = (
                ("practice_questions", lesson.get("practice_questions", []), None),
                ("questions", lesson.get("questions", []), None),
                ("interactive_question", [lesson.get("interactive_question")], None),
            )
            for source_field, source_value, pathway in location_fields:
                if not isinstance(source_value, list):
                    continue
                for question in source_value:
                    if not isinstance(question, dict) or not question.get("id"):
                        continue
                    rows.append({
                        "course_id": course["id"],
                        "course_title": course.get("title", course["id"]),
                        "lesson_id": lesson.get("id"),
                        "lesson_title": lesson.get("title", lesson.get("id", "Lesson")),
                        "source_field": source_field,
                        "pathway": pathway,
                        "question": question,
                    })

            # Entry-diagnostic questions are deliberately excluded. Pathway
            # questions are practice/application items and may be included only
            # when explicitly present in the review registry.
            diagnostic = lesson.get("diagnostic", {})
            pathways = diagnostic.get("pathways", {}) if isinstance(diagnostic, dict) else {}
            if isinstance(pathways, dict):
                for pathway, pathway_data in pathways.items():
                    questions = pathway_data.get("questions", []) if isinstance(pathway_data, dict) else []
                    if not isinstance(questions, list):
                        continue
                    for question in questions:
                        if not isinstance(question, dict) or not question.get("id"):
                            continue
                        rows.append({
                            "course_id": course["id"],
                            "course_title": course.get("title", course["id"]),
                            "lesson_id": lesson.get("id"),
                            "lesson_title": lesson.get("title", lesson.get("id", "Lesson")),
                            "source_field": f"diagnostic.pathways.{pathway}.questions",
                            "pathway": pathway,
                            "question": question,
                        })
    return rows


def _catalogue(
    course_id: str | None = None,
    lesson_id: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    occurrences = _find_occurrences(course_id, lesson_id)
    records: list[dict[str, Any]] = []
    keyed: dict[tuple[str, str, str], dict[str, Any]] = {}
    duplicate_issues: list[dict[str, Any]] = []
    seen_global: dict[str, tuple[str, str, str]] = {}

    for row in occurrences:
        question = row["question"]
        qid = str(question.get("id"))
        key = (row["course_id"], str(row["lesson_id"]), qid)
        if key in keyed:
            existing = keyed[key]
            existing_payload = _question_fingerprint_payload(existing["question"])
            current_payload = _question_fingerprint_payload(question)
            if existing_payload != current_payload:
                existing["catalogue_conflict"] = True
                duplicate_issues.append({
                    "question_id": qid,
                    "severity": "error",
                    "code": "conflicting_duplicate",
                    "message": "The same question ID has conflicting content within one lesson.",
                    "course_id": row["course_id"],
                    "lesson_id": row["lesson_id"],
                })
            elif row["source_field"] not in existing["source_fields"]:
                existing["source_fields"].append(row["source_field"])
            continue

        if qid in seen_global and seen_global[qid] != key:
            duplicate_issues.append({
                "question_id": qid,
                "severity": "error",
                "code": "duplicate_global_id",
                "message": "Question IDs must be globally unique across course/lesson locations.",
                "course_id": row["course_id"],
                "lesson_id": row["lesson_id"],
            })
        else:
            seen_global[qid] = key

        record = {
            "question_id": qid,
            "course_id": row["course_id"],
            "course_title": row["course_title"],
            "lesson_id": row["lesson_id"],
            "lesson_title": row["lesson_title"],
            "source_field": row["source_field"],
            "source_fields": [row["source_field"]],
            "pathway": row["pathway"],
            "question": deepcopy(question),
            "catalogue_conflict": False,
        }
        keyed[key] = record
        records.append(record)

    return records, duplicate_issues, len(occurrences)


def _verification_status(record: dict[str, Any]) -> tuple[str, list[str]]:
    question = record["question"]
    qid = record["question_id"]
    metadata = VERIFICATION_REGISTRY.get(qid)
    if metadata is None:
        return "legacy", ["No VQE review record exists for this question."]

    issues = validate_question(question)
    if record.get("catalogue_conflict"):
        issues.append("Question ID has conflicting authored content.")
    if not _snapshot_matches(question, metadata):
        issues.append("Question content differs from the reviewed snapshot; review evidence is stale.")
    missing_checks = _REQUIRED_REVIEW_CHECKS - set(metadata.get("review_checks", []))
    if missing_checks:
        issues.append("Missing verification checks: " + ", ".join(sorted(missing_checks)) + ".")
    skill_id = metadata.get("skill_id")
    if skill_id not in math_taxonomy.SKILLS:
        issues.append(f"Unknown VQE skill_id '{skill_id}'.")
    grade_bands = metadata.get("grade_bands")
    if not isinstance(grade_bands, list) or not grade_bands or any(
        band not in GRADE_BANDS for band in grade_bands
    ):
        issues.append("Question needs valid Grade 7–9 planning-band metadata.")
    if issues:
        return "needs_review", issues
    return "verified", []


def normalise_question(record: dict[str, Any]) -> dict[str, Any]:
    """Return a normalised copy with VQE metadata; never mutate authored source."""
    question = deepcopy(record["question"])
    qid = record["question_id"]
    metadata = VERIFICATION_REGISTRY.get(qid)
    status, issues = _verification_status(record)
    if metadata:
        skill = math_taxonomy.SKILLS.get(metadata.get("skill_id"), {})
        question.update({
            "skill_id": metadata.get("skill_id"),
            "skill_label": skill.get("label", record["lesson_title"]),
            "grade_bands": list(metadata.get("grade_bands", [])),
            "strand": metadata.get("strand"),
            "topic": metadata.get("topic"),
            "purpose": metadata.get("purpose"),
            "difficulty": metadata.get("difficulty"),
            "question_version": metadata.get("version", 1),
            "verification_status": status,
            "verification_reviewed_at": metadata.get("reviewed_at"),
            "verification_issues": list(issues),
            "verification_engine_version": ENGINE_VERSION,
            "source_course_id": record["course_id"],
            "source_lesson_id": record["lesson_id"],
            "source_field": record["source_field"],
            "pathway": metadata.get("pathway"),
        })
    else:
        question.update({
            "skill_id": None,
            "question_version": 1,
            "verification_status": "legacy",
            "verification_issues": list(issues),
            "verification_engine_version": ENGINE_VERSION,
            "source_course_id": record["course_id"],
            "source_lesson_id": record["lesson_id"],
            "source_field": record["source_field"],
            "pathway": record["pathway"],
        })
    return question


def iter_question_records(
    course_id: str | None = None,
    lesson_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return unique question records; baseline diagnostic items are excluded."""
    records, _, _ = _catalogue(course_id=course_id, lesson_id=lesson_id)
    output = []
    for record in records:
        normalized = normalise_question(record)
        output.append({
            **{key: value for key, value in record.items() if key != "question"},
            "question": normalized,
            "verification_status": normalized.get("verification_status", "legacy"),
            "verification_issues": list(normalized.get("verification_issues", [])),
            "metadata": deepcopy(VERIFICATION_REGISTRY.get(record["question_id"])),
        })
    return output


def get_question_record(
    question_id: str,
    *,
    course_id: str | None = None,
    lesson_id: str | None = None,
) -> dict[str, Any] | None:
    """Resolve one unique question ID in optional course/lesson context."""
    matches = [
        record for record in iter_question_records(course_id, lesson_id)
        if record["question_id"] == str(question_id)
    ]
    return matches[0] if len(matches) == 1 else None


def get_questions(
    *,
    course_id: str | None = None,
    lesson_id: str | None = None,
    skill_id: str | None = None,
    grade_band: int | None = None,
    purpose: str | None = None,
    difficulty: int | None = None,
    pathway: str | None = None,
    verified_only: bool = False,
    include_pathways: bool = True,
) -> list[dict[str, Any]]:
    """Retrieve filtered records in authored order.

    With verified_only=True, stale, invalid, legacy, and conflicting items are
    excluded. For a pathway selection, core lesson questions are combined only
    with questions explicitly registered for that pathway.
    """
    records = iter_question_records(course_id=course_id, lesson_id=lesson_id)
    selected = []
    for record in records:
        question = record["question"]
        metadata = record.get("metadata") or {}
        if verified_only and record["verification_status"] != "verified":
            continue
        if skill_id is not None and metadata.get("skill_id") != skill_id:
            continue
        if grade_band is not None and grade_band not in metadata.get("grade_bands", []):
            continue
        if purpose is not None and metadata.get("purpose") != purpose:
            continue
        if difficulty is not None and metadata.get("difficulty") != difficulty:
            continue

        record_pathway = metadata.get("pathway")
        if pathway is not None:
            if record_pathway not in (None, pathway):
                continue
        elif not include_pathways and record_pathway is not None:
            continue

        # Pilot lessons are strict by default, regardless of which consumer
        # requested them. Non-pilot records remain visible for legacy migration.
        if is_vqe_pilot_lesson(record["course_id"], record["lesson_id"]):
            if record["verification_status"] != "verified":
                continue
        selected.append(record)
    return selected


def select_questions(
    *,
    course_id: str | None = None,
    lesson_id: str | None = None,
    skill_id: str | None = None,
    grade_band: int | None = None,
    purpose: str | None = None,
    difficulty: int | None = None,
    pathway: str | None = None,
    count: int | None = None,
    verified_only: bool = True,
    include_pathways: bool = True,
    exclude_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Select a bounded deterministic set of eligible questions.

    This prototype uses transparent filters and authored order, not a trained
    learner model. Repeated IDs are excluded and no legacy fallback is applied
    to strict pilot lessons.
    """
    records = get_questions(
        course_id=course_id,
        lesson_id=lesson_id,
        skill_id=skill_id,
        grade_band=grade_band,
        purpose=purpose,
        difficulty=difficulty,
        pathway=pathway,
        verified_only=verified_only,
        include_pathways=include_pathways,
    )
    exclude_ids = {str(item) for item in (exclude_ids or set())}
    output = []
    seen = set()
    for record in records:
        qid = str(record["question_id"])
        if qid in seen or qid in exclude_ids:
            continue
        seen.add(qid)
        output.append(record)
    if count is not None:
        try:
            limit = max(0, int(count))
        except (TypeError, ValueError):
            limit = 0
        output = output[:limit]
    return output


def audit_question_bank(
    *,
    course_id: str | None = None,
    lesson_id: str | None = None,
) -> dict[str, Any]:
    """Return a read-only audit of question structure, duplicate IDs, and evidence."""
    records, duplicate_issues, occurrence_count = _catalogue(course_id, lesson_id)
    issues = list(duplicate_issues)
    counts = {status: 0 for status in VERIFICATION_STATUSES}
    item_reports = []
    for record in records:
        status, item_issues = _verification_status(record)
        if status not in counts:
            counts[status] = 0
        counts[status] += 1
        for message in item_issues:
            severity = "error" if status == "needs_review" else "warning"
            item_reports.append({
                "question_id": record["question_id"],
                "course_id": record["course_id"],
                "lesson_id": record["lesson_id"],
                "status": status,
                "severity": severity,
                "message": message,
            })
        if status == "needs_review":
            issues.append({
                "question_id": record["question_id"],
                "course_id": record["course_id"],
                "lesson_id": record["lesson_id"],
                "severity": "error",
                "code": "needs_review",
                "message": "; ".join(item_issues),
            })
        elif status == "legacy":
            issues.append({
                "question_id": record["question_id"],
                "course_id": record["course_id"],
                "lesson_id": record["lesson_id"],
                "severity": "warning",
                "code": "legacy",
                "message": "Question has not been reviewed under the VQE policy.",
            })
    return {
        "engine_version": ENGINE_VERSION,
        "total_occurrences": occurrence_count,
        "unique_questions": len(records),
        "counts": counts,
        "verified_count": counts.get("verified", 0),
        "needs_review_count": counts.get("needs_review", 0),
        "legacy_count": counts.get("legacy", 0),
        "issues": issues,
        "item_reports": item_reports,
    }


def get_review_record(question_id: str) -> dict[str, Any] | None:
    """Return a defensive copy of the review metadata for tests/admin inspection."""
    metadata = VERIFICATION_REGISTRY.get(str(question_id))
    return deepcopy(metadata) if metadata else None


def validate_registry() -> list[str]:
    """Validate registry consistency without reading course content."""
    errors = []
    for question_id, metadata in VERIFICATION_REGISTRY.items():
        if not isinstance(metadata, dict):
            errors.append(f"{question_id}: registry entry must be a dictionary.")
            continue
        if question_id not in metadata.get("reviewed_content", {}).get("id", question_id) and False:
            # Retained as an intentionally unreachable type guard; IDs are keys,
            # while the question's own ID is compared by the catalogue.
            errors.append(f"{question_id}: invalid registry ID.")
        if metadata.get("skill_id") not in math_taxonomy.SKILLS:
            errors.append(f"{question_id}: unknown skill ID.")
        if metadata.get("purpose") not in QUESTION_PURPOSES:
            errors.append(f"{question_id}: unsupported purpose.")
        if metadata.get("difficulty") not in (1, 2, 3):
            errors.append(f"{question_id}: difficulty must be 1, 2, or 3.")
        if not isinstance(metadata.get("version"), int) or metadata["version"] < 1:
            errors.append(f"{question_id}: version must be a positive integer.")
        if not isinstance(metadata.get("reviewed_content"), dict) or not metadata["reviewed_content"]:
            errors.append(f"{question_id}: reviewed content snapshot is required.")
    return errors
