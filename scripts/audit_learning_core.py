"""Read-only baseline audit for Vocogni's learning content and assessment coverage.

Run from the repository root:
    python scripts/audit_learning_core.py
    python scripts/audit_learning_core.py --output artifacts/learning-core-audit.json
    python scripts/audit_learning_core.py --strict

This reports structural and metadata evidence only. It does not establish
mathematical correctness, diagnostic validity, transfer validity, or learning gain.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import data
import diagnostics
import question_engine
import transfer_check


def build_report() -> dict[str, Any]:
    courses = data.all_courses_in_order()
    course_summaries: list[dict[str, Any]] = []
    diagnostic_issues: list[dict[str, str]] = []
    lesson_identity_issues: list[dict[str, str]] = []
    question_totals: Counter[str] = Counter()
    purpose_totals: Counter[str] = Counter()
    difficulty_totals: Counter[str] = Counter()
    skill_totals: Counter[str] = Counter()
    lesson_ids: dict[str, str] = {}

    for course in courses:
        course_id = str(course.get("id") or "")
        lessons = course.get("lessons", [])
        if not isinstance(lessons, list):
            lessons = []
            lesson_identity_issues.append({
                "course_id": course_id,
                "message": "Course lessons must be a list.",
            })

        lesson_summaries: list[dict[str, Any]] = []
        for lesson in lessons:
            lesson_id = str(lesson.get("id") or "")
            identity = f"{course_id}/{lesson_id}"
            if not lesson_id:
                lesson_identity_issues.append({
                    "course_id": course_id,
                    "message": "Lesson is missing a stable ID.",
                })
            elif lesson_id in lesson_ids and lesson_ids[lesson_id] != course_id:
                lesson_identity_issues.append({
                    "course_id": course_id,
                    "message": (
                        f"Lesson ID {lesson_id!r} is also used by "
                        f"{lesson_ids[lesson_id]!r}."
                    ),
                })
            else:
                lesson_ids[lesson_id] = course_id

            audit = question_engine.audit_question_bank(
                course_id=course_id, lesson_id=lesson_id
            )
            counts = audit.get("counts", {})
            for status, count in counts.items():
                question_totals[str(status)] += int(count or 0)

            records = question_engine.iter_question_records(
                course_id=course_id, lesson_id=lesson_id
            )
            for record in records:
                if record.get("verification_status") != "verified":
                    continue
                metadata = record.get("metadata") or {}
                purpose_totals[str(metadata.get("purpose") or "unspecified")] += 1
                difficulty_totals[str(metadata.get("difficulty") or "unspecified")] += 1
                skill_totals[str(metadata.get("skill_id") or "unspecified")] += 1

            diagnostic = lesson.get("diagnostic")
            diagnostic_result: dict[str, Any]
            if diagnostic is None:
                diagnostic_result = {"present": False, "valid": None, "issues": []}
            else:
                errors = diagnostics.validate_diagnostic_config(diagnostic)
                diagnostic_result = {
                    "present": True,
                    "valid": not errors,
                    "question_count": len(diagnostic.get("questions", []))
                    if isinstance(diagnostic, dict)
                    and isinstance(diagnostic.get("questions"), list)
                    else 0,
                    "issues": errors,
                }
                for error in errors:
                    diagnostic_issues.append({
                        "course_id": course_id,
                        "lesson_id": lesson_id,
                        "message": error,
                    })

            lesson_summaries.append({
                "lesson_id": lesson_id,
                "lesson_title": lesson.get("title", lesson_id),
                "question_bank": {
                    "total_occurrences": audit.get("total_occurrences", 0),
                    "unique_questions": audit.get("unique_questions", 0),
                    "counts": counts,
                    "issues": audit.get("issues", []),
                },
                "diagnostic": diagnostic_result,
            })

        course_summaries.append({
            "course_id": course_id,
            "course_title": course.get("title", course_id),
            "lesson_count": len(lessons),
            "lessons": lesson_summaries,
        })

    registry_errors = question_engine.validate_registry()
    global_question_audit = question_engine.audit_question_bank()
    global_duplicate_errors = [
        issue for issue in global_question_audit.get("issues", [])
        if issue.get("code") in ("duplicate_global_id", "conflicting_duplicate")
    ]
    transfer = transfer_check.audit_transfer_coverage()

    question_bank_errors = sum(
        int(item.get("needs_review_count", 0))
        for course in courses
        for lesson in course.get("lessons", [])
        for item in [
            question_engine.audit_question_bank(
                course_id=str(course.get("id") or ""),
                lesson_id=str(lesson.get("id") or ""),
            )
        ]
    )

    error_count = (
        len(registry_errors)
        + len(diagnostic_issues)
        + len(lesson_identity_issues)
        + question_bank_errors
        + len(global_duplicate_errors)
    )
    warning_count = int(question_totals.get("legacy", 0))

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "static course content and learning-engine metadata",
        "summary": {
            "course_count": len(courses),
            "lesson_count": sum(item["lesson_count"] for item in course_summaries),
            "question_status_counts": dict(sorted(question_totals.items())),
            "verified_questions_by_purpose": dict(sorted(purpose_totals.items())),
            "verified_questions_by_difficulty": dict(sorted(difficulty_totals.items())),
            "verified_questions_by_skill": dict(sorted(skill_totals.items())),
            "registry_error_count": len(registry_errors),
            "diagnostic_error_count": len(diagnostic_issues),
            "lesson_identity_error_count": len(lesson_identity_issues),
            "question_needs_review_count": question_bank_errors,
            "global_duplicate_question_error_count": len(global_duplicate_errors),
            "legacy_question_warning_count": warning_count,
            "transfer_coverage": {
                key: value
                for key, value in transfer.items()
                if key != "rows"
            },
            "error_count": error_count,
            "warning_count": warning_count,
        },
        "registry_errors": registry_errors,
        "global_question_bank_issues": global_question_audit.get("issues", []),
        "diagnostic_issues": diagnostic_issues,
        "lesson_identity_issues": lesson_identity_issues,
        "transfer_coverage": transfer,
        "courses": course_summaries,
        "limitations": [
            "Structural validation does not prove mathematical correctness.",
            "A verified registry record reflects the repository's review contract, not an independent re-review by this script.",
            "Diagnostic configuration validity does not establish diagnostic reliability or construct validity.",
            "Cross-lesson application coverage does not prove that an item measures genuine transfer.",
            "This audit does not measure learner outcomes or inspect live authentication, persistence, or UI behavior.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional path for a JSON report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when structural errors are found.",
    )
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Audit report written to {args.output}")
    else:
        print(rendered)

    summary = report["summary"]
    print(
        "\nAudit summary: "
        f"{summary['course_count']} courses, "
        f"{summary['lesson_count']} lessons, "
        f"{sum(summary['question_status_counts'].values())} unique questions, "
        f"{summary['error_count']} errors, "
        f"{summary['warning_count']} legacy warnings."
    )
    return 1 if args.strict and summary["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
