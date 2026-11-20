"""Audit release-evidence records without treating paperwork as legal compliance.

This audit checks checklist integrity only. It cannot validate evidence truth,
reviewer identity/qualification, or legal sufficiency.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "legal" / "release-evidence.template.json"

REQUIRED_ITEMS = {
    "responsible_operator": "Identified responsible operator/controller and operational authority",
    "privacy_notice_final": "Privacy notice accurately describes deployed processing and is approved",
    "terms_final": "Terms are final, operator-specific, and legally reviewed",
    "child_protection_assessment": "Child-specific product/feature risk assessment and mitigation reviewed",
    "age_assurance": "Age-band/eligibility decision and user-verification mechanism implemented and tested",
    "guardian_consent": "Required guardian consent, verification, recording, withdrawal, and refusal handling implemented",
    "data_inventory_and_lawful_basis": "Data inventory, purposes, lawful bases, necessity, and minimisation reconciled with production",
    "vendor_and_transfer_review": "Actual providers, contracts, subprocessors, regions, and transfers reviewed",
    "retention_and_deletion": "Retention schedule, deletion, backup-expiry, and provider-side handling implemented/tested",
    "data_rights_workflow": "Access/correction/deletion/withdrawal and child/guardian requests have a tested private workflow",
    "database_access_controls": "Production access control, RLS/grants, secrets, and cross-account isolation independently tested",
    "incident_response": "Monitored support/reporting channels and privacy/child-safety incident procedure tested",
    "pse_registration_assessment": "PSE registration applicability assessed; required registration/permit evidence obtained if applicable",
    "deployment_acceptance": "Deployed commit matches reviewed commit; synthetic-data acceptance tests passed",
    "external_ai_review": "Optional AI provider/data flow/contract/safety reviewed; or counsel-reviewed non-applicability decision",
}
ALLOWED_STATUSES = {"pending", "in_review", "approved", "not_applicable"}
NOT_APPLICABLE_ALLOWED = {"external_ai_review"}


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return parsed.isoformat() == value and parsed <= date.today()


def validate_manifest(manifest: Any) -> dict[str, Any]:
    """Return blockers/warnings; missing records are never assumed cleared."""
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(manifest, dict):
        blockers = [{"item": key, "reason": "Manifest must be a JSON object."} for key in REQUIRED_ITEMS]
        return {
            "schema_version": 1, "item_count": len(REQUIRED_ITEMS),
            "approved_count": 0, "resolved_count": 0,
            "blocker_count": len(blockers), "warning_count": 1,
            "ready_for_adult_legal_and_operator_review": False,
            "blockers": blockers,
            "warnings": [{"reason": "Invalid manifest shape; no entries evaluated."}],
            "limitations": ["This report is not a compliance determination."],
        }

    if manifest.get("schema_version") != 1:
        blockers.append({"item": "schema_version", "reason": "Expected schema_version 1."})
    entries = manifest.get("items")
    if not isinstance(entries, dict):
        entries = {}
        blockers.append({"item": "items", "reason": "Expected an items object."})

    for key in sorted(set(entries) - set(REQUIRED_ITEMS)):
        warnings.append({"item": key, "reason": "Unknown evidence key; ignored."})

    approved_count = 0
    resolved_count = 0
    for key in REQUIRED_ITEMS:
        entry = entries.get(key)
        if not isinstance(entry, dict):
            blockers.append({"item": key, "reason": "Missing evidence record."})
            continue
        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            blockers.append({"item": key, "reason": "Invalid status value."})
            continue
        if status in ("pending", "in_review"):
            blockers.append({"item": key, "reason": "Evidence is not approved."})
            continue
        if status == "not_applicable":
            if key not in NOT_APPLICABLE_ALLOWED:
                blockers.append({"item": key, "reason": "Not-applicable is prohibited for this release requirement."})
                continue
            if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
                blockers.append({"item": key, "reason": "Not-applicable requires a rationale."})
                continue
            if entry.get("reviewer_role") != "qualified_indonesian_counsel":
                blockers.append({"item": key, "reason": "Not-applicable requires qualified Indonesian counsel review."})
                continue

        metadata = {
            "reviewed_by": entry.get("reviewed_by"),
            "reviewer_role": entry.get("reviewer_role"),
            "reviewed_on": entry.get("reviewed_on"),
            "evidence_ref": entry.get("evidence_ref"),
            "scope": entry.get("scope"),
        }
        missing = [name for name, value in metadata.items()
                   if not isinstance(value, str) or not value.strip()]
        if missing:
            blockers.append({"item": key, "reason": "Missing review metadata: " + ", ".join(missing)})
            continue
        if not _valid_date(entry.get("reviewed_on")):
            blockers.append({"item": key, "reason": "reviewed_on must be a valid ISO date and cannot be future-dated."})
            continue

        if status == "approved":
            approved_count += 1
            resolved_count += 1
        elif status == "not_applicable":
            resolved_count += 1

    return {
        "schema_version": 1,
        "item_count": len(REQUIRED_ITEMS),
        "approved_count": approved_count,
        "resolved_count": resolved_count,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "ready_for_adult_legal_and_operator_review": not blockers and not warnings,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": [
            "This tool checks record completeness and dates only, not whether evidence is genuine, sufficient, legally correct, or implemented in production.",
            "Reviewer names/roles are self-reported and are not identity-verified by this script.",
            "Passing this audit is not legal clearance or permission to enable learner access.",
            "Public launch requires responsible adult operator and qualified Indonesian legal review; this tool cannot grant either.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when blockers or warnings exist.")
    parser.add_argument("--output", type=Path, help="Optional JSON report output path.")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = validate_manifest(None)
        report["warnings"].append({"reason": f"Unable to read manifest: {exc}"})
        report["ready_for_adult_legal_and_operator_review"] = False
    else:
        report = validate_manifest(manifest)

    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Legal release-evidence audit written to {args.output}")
    else:
        print(rendered)
    print(
        f"Release evidence: {report['resolved_count']}/{report['item_count']} resolved "
        f"({report['approved_count']} approved); {report['blocker_count']} blockers; "
        f"{report['warning_count']} warnings."
    )
    if args.strict and (report["blocker_count"] or report["warning_count"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
