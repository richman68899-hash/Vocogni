"""
diagnostics.py — reusable, transparent lesson diagnostic engine for Vocogni v1.4.

This is a rule-based, explainable prototype ("AI-style" decision support), not a
trained machine-learning model or a validated psychometric assessment.
Lesson authors provide five consistently tagged items:
prerequisite, level_1, level_2, level_3, project.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import logic
import question_engine

REQUIRED_STAGES = ("prerequisite", "level_1", "level_2", "level_3", "project")

PLACEMENT = {
    "prerequisite": {
        "label": "Prerequisite review recommended",
        "level": "Prerequisite",
        "summary": "A foundational concept needs attention before progressing.",
        "next_action": "Review the prerequisite explanation, then begin the lesson's supported practice.",
    },
    "level_1": {
        "label": "Start at Level 1 — Easy",
        "level": "Level 1",
        "summary": "Build confidence with the core idea and straightforward examples.",
        "next_action": "Begin the lesson's introductory practice.",
    },
    "level_2": {
        "label": "Start at Level 2 — Medium",
        "level": "Level 2",
        "summary": "The starting knowledge supports practice with a moderate step up.",
        "next_action": "Work through the medium-level questions.",
    },
    "level_3": {
        "label": "Start at Level 3 — Hard",
        "level": "Level 3",
        "summary": "The result supports trying more demanding multi-step questions.",
        "next_action": "Work through the harder questions and check the reasoning carefully.",
    },
    "project": {
        "label": "Start with a real-life project",
        "level": "Project",
        "summary": "All diagnostic items were answered correctly; try applying the concept in context.",
        "next_action": "Complete the real-life application task.",
    },
}


PATHWAY_META = {
    "level_1": {"label": "Level 1 — Easy", "description": "Core concepts and supported examples."},
    "level_2": {"label": "Level 2 — Medium", "description": "Moderate practice that builds on the core idea."},
    "level_3": {"label": "Level 3 — Hard", "description": "More demanding, multi-step reasoning."},
    "project": {"label": "Real-life project", "description": "Apply the concept in a practical situation."},
}


def unlocked_pathways_for_score(result: dict[str, Any]) -> list[str]:
    """Return cumulative practice pathways unlocked by a saved diagnostic.

    A missed prerequisite gates the learner to Level 1. Otherwise:
    1-2/5 -> Level 1; 3/5 -> Levels 1-2; 4/5 -> Levels 1-3;
    5/5 -> Levels 1-3 and Project.
    """
    if not result.get("prerequisite_correct", False):
        return ["level_1"]
    score = int(result.get("score", 0))
    if score >= 5:
        return ["level_1", "level_2", "level_3", "project"]
    if score >= 4:
        return ["level_1", "level_2", "level_3"]
    if score >= 3:
        return ["level_1", "level_2"]
    return ["level_1"]


def validate_diagnostic_config(config: Any) -> list[str]:
    """Return configuration errors; an empty list means the schema is structurally valid."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["Diagnostic must be a dictionary."]
    questions = config.get("questions")
    if not isinstance(questions, list) or len(questions) != 5:
        errors.append("Diagnostic must contain exactly five questions.")
        questions = questions if isinstance(questions, list) else []
    seen_ids: set[str] = set()
    seen_stages: list[str] = []
    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            errors.append(f"Question {index} must be a dictionary.")
            continue
        # Apply the shared VQE structural checks, then retain diagnostic-
        # specific stage/skill/pathway rules below. The default grader matches
        # the pre-existing diagnostic convention for chemistry items.
        default_grader = "math" if question.get("grader") == "math" else "chemistry"
        for item_error in question_engine.validate_question(
            question, default_grader=default_grader
        ):
            errors.append(f"Question {index}: {item_error}.")
        for field in ("id", "prompt", "type", "answer", "stage", "skill_tag", "explanation"):
            if field not in question:
                errors.append(f"Question {index} is missing '{field}'.")
        qid = question.get("id")
        if not isinstance(qid, str) or not qid:
            errors.append(f"Question {index} needs a stable string ID.")
        elif qid in seen_ids:
            errors.append(f"Duplicate question ID: {qid}.")
        else:
            seen_ids.add(qid)
        stage = question.get("stage")
        if stage not in REQUIRED_STAGES:
            errors.append(f"Question {index} has unknown stage '{stage}'.")
        else:
            seen_stages.append(stage)
        if not isinstance(question.get("skill_tag"), str) or not question.get("skill_tag", "").strip():
            errors.append(f"Question {index} needs a non-empty skill_tag.")
        if question.get("type") == "mc" and (
            not isinstance(question.get("options"), list)
            or question.get("answer") not in question.get("options", [])
        ):
            errors.append(f"Question {index} has invalid multiple-choice options/answer.")
        if question.get("type") == "open_ended":
            if question.get("grader") == "math":
                import math_grading
                grader = math_grading
            else:
                import chemistry_grading
                grader = chemistry_grading
            for rubric_error in grader.validate_open_response_question(question):
                errors.append(f"Question {index}: {rubric_error}.")
        elif question.get("type") not in ("mc", "numeric"):
            errors.append(f"Question {index} has unsupported type '{question.get('type')}'.")
    if set(seen_stages) != set(REQUIRED_STAGES) or len(seen_stages) != len(set(seen_stages)):
        errors.append("Use each required stage exactly once: prerequisite, level_1, level_2, level_3, project.")
    if not isinstance(config.get("prerequisite_review"), str) or not config.get("prerequisite_review", "").strip():
        errors.append("Provide prerequisite_review text.")
    pathways = config.get("pathways")
    if not isinstance(pathways, dict):
        errors.append("Provide pathways for level_2, level_3, and project.")
    else:
        for key in ("level_2", "level_3", "project"):
            pathway = pathways.get(key)
            if not isinstance(pathway, dict) or not isinstance(pathway.get("questions"), list) or not pathway["questions"]:
                errors.append(f"Pathway '{key}' needs at least one question.")
    return errors


def _is_correct(question: dict[str, Any], answer: Any) -> bool:
    if answer is None or (isinstance(answer, str) and not answer.strip()):
        return False
    return bool(logic.check_answer(question, answer))


def evaluate_diagnostic(config: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    """Score one submitted attempt and return an auditable explanation of placement."""
    errors = validate_diagnostic_config(config)
    if errors:
        raise ValueError("Invalid diagnostic configuration: " + " ".join(errors))

    review: list[dict[str, Any]] = []
    correct_count = 0
    marks_awarded = 0
    maximum_marks = 0
    prerequisite_correct = False
    for question in config["questions"]:
        answer = answers.get(question["id"])
        marking = None
        if question.get("type") == "open_ended":
            if question.get("grader") == "math":
                import math_grading
                grader = math_grading
            else:
                import chemistry_grading
                grader = chemistry_grading
            marking = grader.evaluate_open_response(question, answer)
            correct = bool(marking["full_credit"])
            marks_awarded += int(marking["score"])
            maximum_marks += int(marking["max_marks"])
        else:
            correct = _is_correct(question, answer)
            marks_awarded += int(correct)
            maximum_marks += 1
        correct_count += int(correct)
        if question["stage"] == "prerequisite":
            prerequisite_correct = correct
        item = {
            "question_id": question["id"],
            "stage": question["stage"],
            "skill_tag": question["skill_tag"],
            "prompt": question["prompt"],
            "user_answer": answer,
            "expected_answer": question["answer"],
            "correct": correct,
            "explanation": question["explanation"],
        }
        if marking:
            item.update({
                "marks_awarded": marking["score"],
                "max_marks": marking["max_marks"],
                "mark_percent": marking["percent"],
                "marking_points": marking["marking_points"],
                "typo_warning": marking["typo_warning"],
                "marking_feedback": marking["feedback"],
            })
        review.append(item)

    total = len(config["questions"])
    percent = round(correct_count / total * 100)
    # Foundational prerequisite failure takes priority: advanced answers can
    # otherwise mask a gap that prevents secure learning of the target concept.
    if not prerequisite_correct:
        outcome_key = "prerequisite"
        placement_reason = "The prerequisite check was incorrect, so the system recommends reviewing the foundation first."
    elif correct_count == 5:
        outcome_key = "project"
        placement_reason = "All five diagnostic items were correct, including the project-readiness item."
    elif correct_count == 4:
        outcome_key = "level_3"
        placement_reason = "Four of five items were correct and the prerequisite check passed."
    elif correct_count == 3:
        outcome_key = "level_2"
        placement_reason = "Three of five items were correct and the prerequisite check passed."
    else:
        outcome_key = "level_1"
        placement_reason = "The prerequisite check passed, but the overall score suggests starting with supported core practice."

    weaknesses = []
    for item in review:
        if not item["correct"]:
            weakness = {
                "skill_tag": item["skill_tag"],
                "question_id": item["question_id"],
                "stage": item["stage"],
                "why_flagged": "The learner's response did not match the expected answer.",
                "recommended_action": (
                    config.get("prerequisite_review", "")
                    if item["stage"] == "prerequisite"
                    else f"Review the explanation for: {item['skill_tag']}."
                ),
            }
            if not any(w["skill_tag"] == weakness["skill_tag"] for w in weaknesses):
                weaknesses.append(weakness)

    placement = PLACEMENT[outcome_key]
    return {
        "score": correct_count,
        "total": total,
        "percent": percent,
        "marks_awarded": marks_awarded,
        "max_marks": maximum_marks,
        "mark_percent": round(marks_awarded / maximum_marks * 100) if maximum_marks else 0,
        "outcome_key": outcome_key,
        "unlocked_pathways": unlocked_pathways_for_score({
            "score": correct_count,
            "prerequisite_correct": prerequisite_correct,
        }),
        "outcome_label": placement["label"],
        "outcome_level": placement["level"],
        "outcome_summary": placement["summary"],
        "next_action": placement["next_action"],
        "placement_reason": placement_reason,
        "prerequisite_correct": prerequisite_correct,
        "weaknesses": weaknesses,
        "answer_review": review,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": "1.4-rule-based-1",
        "diagnostic_version": config.get("version", 1),
        "pathway_started_at": None,
    }


def get_pathway_questions(lesson: dict[str, Any], outcome_key: str) -> list[dict[str, Any]]:
    """Return the question set for a placement; Level 1 uses the lesson's existing questions."""
    if outcome_key in ("prerequisite", "level_1"):
        if outcome_key == "prerequisite":
            # Scaffolded pathway: use the lesson's existing core practice after
            # displaying prerequisite_review; don't duplicate the question bank.
            return lesson.get("questions", [])
        return lesson.get("questions", [])
    pathway = lesson.get("diagnostic", {}).get("pathways", {}).get(outcome_key, {})
    questions = pathway.get("questions", [])
    return questions if isinstance(questions, list) and questions else lesson.get("questions", [])


def summarize_weaknesses(result: dict[str, Any]) -> list[str]:
    """Return unique, human-readable weak-skill labels from the saved result."""
    return list(dict.fromkeys(
        str(item.get("skill_tag", "Unclassified skill"))
        for item in result.get("weaknesses", [])
        if item.get("skill_tag")
    ))


def unlocked_pathways_for_score(result: dict[str, Any]) -> list[str]:
    """Return cumulative practice routes unlocked by a saved diagnostic result.

    A failed prerequisite gates progression to Level 1 only. Otherwise, the
    score unlocks a cumulative set of routes: 1-2 -> L1; 3 -> L1-L2;
    4 -> L1-L3; 5 -> L1-L3 plus project.
    """
    if not result.get("prerequisite_correct", False):
        return ["level_1"]
    score = int(result.get("score", 0))
    if score >= 5:
        return ["level_1", "level_2", "level_3", "project"]
    if score >= 4:
        return ["level_1", "level_2", "level_3"]
    if score >= 3:
        return ["level_1", "level_2"]
    return ["level_1"]
