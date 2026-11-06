"""Command-line report for verified cross-lesson transfer-question coverage.

Run from the repository root:
    python audit_transfer_coverage.py
    python audit_transfer_coverage.py --course fractions
    python audit_transfer_coverage.py --uncovered-only
    python audit_transfer_coverage.py --json

This reports catalogue metadata coverage only. It does not establish that an
item is unfamiliar to learners or that it validly measures learning transfer.
"""
from __future__ import annotations

import argparse
import json

import transfer_check


def build_report(*, course_id: str | None = None) -> dict:
    """Return the coverage audit, optionally restricted to one course."""
    report = transfer_check.audit_transfer_coverage()
    rows = report["rows"]
    if course_id:
        rows = [row for row in rows if row["course_id"] == course_id]

    covered = sum(bool(row["has_cross_lesson_application_item"]) for row in rows)
    total = len(rows)
    return {
        "scope": "catalogue_metadata_only",
        "practice_course_skill_pairs": total,
        "covered_pairs": covered,
        "uncovered_pairs": total - covered,
        "coverage_percent": round(covered / total * 100) if total else 0,
        "rows": rows,
    }


def render_report(report: dict, *, uncovered_only: bool = False) -> str:
    """Render a concise human-readable report."""
    lines = [
        "VOCogni — INDEPENDENT TRANSFER COVERAGE",
        (
            f"Coverage: {report['covered_pairs']}/{report['practice_course_skill_pairs']} "
            f"course-skill pairs ({report['coverage_percent']}%)"
        ),
        f"Uncovered pairs: {report['uncovered_pairs']}",
        "",
        "Pair details:",
    ]
    rows = report["rows"]
    if uncovered_only:
        rows = [row for row in rows if not row["has_cross_lesson_application_item"]]
    if not rows:
        lines.append("  No matching course-skill pairs.")
    for row in rows:
        status = "COVERED" if row["has_cross_lesson_application_item"] else "UNCOVERED"
        lines.append(f"- [{status}] {row['course_id']} / {row['skill_id']}")
        lines.append(
            "  Practice lessons: " + ", ".join(row["practice_lesson_ids"])
        )
        question_ids = row["application_question_ids"]
        lines.append(
            "  Eligible cross-lesson application items: "
            + (", ".join(question_ids) if question_ids else "none")
        )
    lines.extend([
        "",
        "Interpretation: coverage means at least one verified application item is",
        "authored in a different lesson. It does not prove novelty, question quality,",
        "valid transfer measurement, or improved learning outcomes.",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course", help="Limit the report to a course ID.")
    parser.add_argument(
        "--uncovered-only",
        action="store_true",
        help="Show only uncovered pairs (summary totals still cover the selected scope).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the structured report as JSON.",
    )
    args = parser.parse_args()

    report = build_report(course_id=args.course)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_report(report, uncovered_only=args.uncovered_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
