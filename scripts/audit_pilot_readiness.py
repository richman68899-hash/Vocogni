"""Read-only readiness audit for Vocogni's strict VQE pilot lessons.

This checks instructional structure and reviewed-question coverage. It does not
prove mathematical correctness, independent review, learner usability, or
learning effectiveness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import data
import question_engine


def audit_lesson(course_id: str, lesson: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit one pilot lesson using current VQE records."""
    lesson_id = str(lesson.get("id") or "")
    errors: list[str] = []
    warnings: list[str] = []

    for field in ("id", "title", "explanation"):
        value = lesson.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing required lesson field: {field}.")

    worked_example = lesson.get("worked_example")
    if not isinstance(worked_example, str) or not worked_example.strip():
        warnings.append("No authored worked example is present.")

    verified = [
        item for item in records
        if item.get("verification_status") == "verified"
        and item.get("course_id") == course_id
        and item.get("lesson_id") == lesson_id
    ]
    practice = [
        item for item in verified
        if (item.get("question") or {}).get("purpose") == "practice"
    ]
    application = [
        item for item in verified
        if (item.get("question") or {}).get("purpose") in ("application", "reasoning")
    ]

    if len(verified) < 2:
        errors.append(
            f"Only {len(verified)} verified questions; at least 2 are required for a pilot lesson."
        )
    if len(practice) < 2:
        errors.append(
            f"Only {len(practice)} verified practice questions; at least 2 are required."
        )
    if not application:
        warnings.append(
            "No verified application/reasoning question is available; transfer evidence is limited."
        )

    missing_skill = [
        item.get("question_id")
        for item in verified
        if not isinstance((item.get("question") or {}).get("skill_id"), str)
        or not (item.get("question") or {}).get("skill_id")
    ]
    if missing_skill:
        errors.append(
            "Verified questions are missing stable skill IDs: "
            + ", ".join(str(value) for value in missing_skill)
        )

    return {
        "course_id": course_id,
        "lesson_id": lesson_id,
        "lesson_title": lesson.get("title") or lesson_id,
        "verified_question_count": len(verified),
        "verified_practice_count": len(practice),
        "verified_application_or_reasoning_count": len(application),
        "errors": errors,
        "warnings": warnings,
        "ready_for_structural_pilot_review": not errors,
    }


def build_report() -> dict[str, Any]:
    """Build a read-only report for all VQE pilot lessons."""
    records = question_engine.iter_question_records()
    rows = []
    for course_id, lesson_id in sorted(question_engine.PILOT_LESSONS):
        course = data.get_course(course_id)
        if not course:
            rows.append({
                "course_id": course_id,
                "lesson_id": lesson_id,
                "lesson_title": lesson_id,
                "verified_question_count": 0,
                "verified_practice_count": 0,
                "verified_application_or_reasoning_count": 0,
                "errors": ["Pilot lesson references an unknown course."],
                "warnings": [],
                "ready_for_structural_pilot_review": False,
            })
            continue
        lesson = next(
            (item for item in course.get("lessons", []) if item.get("id") == lesson_id),
            None,
        )
        if lesson is None:
            rows.append({
                "course_id": course_id,
                "lesson_id": lesson_id,
                "lesson_title": lesson_id,
                "verified_question_count": 0,
                "verified_practice_count": 0,
                "verified_application_or_reasoning_count": 0,
                "errors": ["Pilot lesson ID is missing from the course catalogue."],
                "warnings": [],
                "ready_for_structural_pilot_review": False,
            })
            continue
        rows.append(audit_lesson(course_id, lesson, records))

    error_count = sum(len(item["errors"]) for item in rows)
    warning_count = sum(len(item["warnings"]) for item in rows)
    return {
        "schema_version": 1,
        "scope": "static structure and VQE coverage for strict pilot lessons",
        "pilot_lesson_count": len(rows),
        "structurally_ready_lesson_count": sum(
            item["ready_for_structural_pilot_review"] for item in rows
        ),
        "error_count": error_count,
        "warning_count": warning_count,
        "lessons": rows,
        "limitations": [
            "A VQE verified status reflects the repository review contract, not independent external subject-matter review.",
            "Structural completeness does not prove mathematical correctness or curriculum alignment.",
            "Application/reasoning metadata does not prove genuine transfer.",
            "This audit does not test the live UI, persistence, devices, or learner outcomes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when structural errors exist.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Pilot readiness report written to {args.output}")
    else:
        print(rendered)
    print(
        "\nPilot readiness: "
        f"{report['structurally_ready_lesson_count']}/{report['pilot_lesson_count']} "
        f"lessons structurally ready; {report['error_count']} errors; "
        f"{report['warning_count']} warnings."
    )
    return 1 if args.strict and report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
