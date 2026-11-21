"""Audit Vocogni's legal-system control register.

This checks document presence and evidence-record completeness only. It cannot
verify evidence truth, legal sufficiency, reviewer identity, production settings,
or grant authority to launch. release_authorized is ALWAYS False.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "docs" / "legal" / "operational-control-register.template.json"

# (control id, required reviewer role, whether counsel may approve N/A)
REQUIRED_CONTROLS: dict[str, tuple[str, str, bool]] = {
    "responsible_operator": ("GOV-01", "responsible_adult_operator", False),
    "ppdp_function": ("GOV-02", "responsible_adult_operator", False),
    "safeguarding_contact": ("GOV-03", "responsible_adult_operator", False),
    "processing_register": ("PROC-01", "ppdp_or_data_protection_function", False),
    "lawful_basis_and_minimisation": ("PROC-02", "qualified_indonesian_counsel", False),
    "age_band_and_eligibility": ("CHILD-01", "qualified_indonesian_counsel", False),
    "age_assurance": ("CHILD-02", "independent_security_reviewer", False),
    "guardian_authorisation": ("CHILD-03", "qualified_indonesian_counsel", False),
    "child_protection_risk_profile": ("CHILD-04", "qualified_indonesian_counsel", False),
    "privacy_by_default": ("CHILD-05", "independent_security_reviewer", False),
    "article_19_profiling": ("PROFILE-01", "qualified_indonesian_counsel", False),
    "child_dpia": ("DPIA-01", "qualified_indonesian_counsel", False),
    "privacy_notice": ("NOTICE-01", "qualified_indonesian_counsel", False),
    "terms_and_acceptance": ("NOTICE-02", "qualified_indonesian_counsel", False),
    "data_rights_workflow": ("RIGHTS-01", "responsible_adult_operator", False),
    "retention_and_deletion": ("LIFE-01", "independent_security_reviewer", False),
    "vendor_contracts_and_security": ("VENDOR-01", "qualified_indonesian_counsel", False),
    "international_transfer": ("TRANSFER-01", "qualified_indonesian_counsel", False),
    "database_and_account_isolation": ("SEC-01", "independent_security_reviewer", False),
    "incident_response": ("INC-01", "responsible_adult_operator", False),
    "pse_registration": ("PSE-01", "qualified_indonesian_counsel", False),
    "external_ai_review": ("AI-01", "qualified_indonesian_counsel", True),
    "school_deployment": ("SCHOOL-01", "qualified_indonesian_counsel", True),
    "deployment_acceptance": ("REL-01", "independent_security_reviewer", False),
    "adult_release_approval": ("REL-02", "responsible_adult_operator", False),
}

REQUIRED_DOCUMENTS = (
    "docs/legal/compliance-operating-system.md",
    "docs/legal/child-access-and-consent-procedure.md",
    "docs/legal/data-rights-procedure.md",
    "docs/legal/incident-response.md",
    "docs/legal/retention-and-deletion.md",
    "docs/legal/vendor-and-transfer-review.md",
    "docs/legal/impact-assessment.template.md",
    "docs/legal/processing-register.template.json",
    "docs/legal/vendor-transfer-register.template.json",
    "docs/legal/operational-control-register.template.json",
    "docs/legal/launch-readiness.md",
    "PRIVACY_POLICY.md",
)

STATUSES = {"pending", "in_review", "approved", "not_applicable", "blocked"}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def validate_register(register: Any, root: Path = ROOT) -> dict[str, Any]:
    """Return integrity blockers. Never return release permission."""
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(register, dict):
        register = {}
        blockers.append({"item": "register", "reason": "Expected a JSON object."})

    if register.get("schema_version") != 1:
        blockers.append({"item": "schema_version", "reason": "Expected schema_version 1."})

    release = register.get("release")
    if not isinstance(release, dict):
        release = {}
        blockers.append({"item": "release", "reason": "Expected a release metadata object."})

    for field in ("release_name", "environment_reference", "review_cycle"):
        if not isinstance(release.get(field), str) or not release[field].strip():
            blockers.append({"item": f"release.{field}", "reason": "A non-empty value is required."})

    if not isinstance(release.get("release_commit_sha"), str) or not SHA_RE.fullmatch(
        release.get("release_commit_sha", "").strip()
        if isinstance(release.get("release_commit_sha"), str) else ""
    ):
        blockers.append({"item": "release.release_commit_sha", "reason": "Record the exact 40-character release commit SHA."})

    for field in ("intended_age_bands", "feature_scope"):
        value = release.get(field)
        if not isinstance(value, list) or not value or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            blockers.append({"item": f"release.{field}", "reason": "A non-empty list of explicit release scope is required."})

    for relative in REQUIRED_DOCUMENTS:
        if not (root / relative).is_file():
            blockers.append({"item": relative, "reason": "Required legal-system document is missing."})

    controls = register.get("controls")
    if not isinstance(controls, dict):
        controls = {}
        blockers.append({"item": "controls", "reason": "Expected a controls object."})

    unknown = sorted(set(controls) - set(REQUIRED_CONTROLS))
    for key in unknown:
        warnings.append({"item": key, "reason": "Unknown control key; not counted toward completion."})

    approved_count = 0
    resolved_count = 0
    for key, (control_id, required_role, na_allowed) in REQUIRED_CONTROLS.items():
        entry = controls.get(key)
        if not isinstance(entry, dict):
            blockers.append({"item": key, "reason": "Missing mandatory control record."})
            continue

        if entry.get("control_id") != control_id:
            blockers.append({"item": key, "reason": f"Expected control_id {control_id}."})
        status = entry.get("status")
        if status not in STATUSES:
            blockers.append({"item": key, "reason": "Invalid or missing status."})
            continue
        if status in {"pending", "in_review", "blocked"}:
            blockers.append({"item": key, "reason": f"Control status is {status}; approval is required."})
            continue
        if status == "not_applicable":
            if not na_allowed:
                blockers.append({"item": key, "reason": "Not-applicable is not permitted for this mandatory control."})
                continue
            if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
                blockers.append({"item": key, "reason": "Not-applicable requires a written rationale."})
                continue

        metadata_fields = (
            "reviewed_by", "reviewer_role", "reviewed_on", "review_due",
            "evidence_ref", "scope", "reviewed_commit_sha"
        )
        missing = [
            name for name in metadata_fields
            if not isinstance(entry.get(name), str) or not entry[name].strip()
        ]
        if missing:
            blockers.append({"item": key, "reason": "Missing review metadata: " + ", ".join(missing)})
            continue

        if entry.get("reviewer_role") != required_role:
            blockers.append({"item": key, "reason": f"Expected reviewer_role {required_role}."})
            continue

        reviewed_on = _iso_date(entry.get("reviewed_on"))
        review_due = _iso_date(entry.get("review_due"))
        if reviewed_on is None or reviewed_on > date.today():
            blockers.append({"item": key, "reason": "reviewed_on must be a valid date no later than today."})
            continue
        if review_due is None or review_due <= date.today():
            blockers.append({"item": key, "reason": "review_due must be a valid future ISO date."})
            continue
        if not SHA_RE.fullmatch(entry.get("reviewed_commit_sha", "")):
            blockers.append({"item": key, "reason": "reviewed_commit_sha must be a 40-character Git commit SHA."})
            continue

        if status == "approved":
            approved_count += 1
            resolved_count += 1
        else:
            resolved_count += 1

    return {
        "schema_version": 1,
        "control_count": len(REQUIRED_CONTROLS),
        "approved_count": approved_count,
        "resolved_count": resolved_count,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "control_register_complete_for_human_review": not blockers and not warnings,
        "release_authorized": False,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": [
            "This tool checks document presence and register structure/metadata only.",
            "Evidence references, reviewer identities, qualifications, and legal conclusions are not independently verified.",
            "It does not inspect production configuration, deployed data flows, contracts, consent records, or infrastructure.",
            "A complete register does not constitute legal clearance, operator approval, or permission to launch.",
            "Public child-facing access must remain blocked until the responsible adult operator and qualified Indonesian counsel approve the exact release.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when blockers or warnings exist.")
    parser.add_argument("--output", type=Path, help="Optional JSON report output path.")
    args = parser.parse_args()

    try:
        register = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        register = None
        read_error = str(exc)
    else:
        read_error = None

    report = validate_register(register)
    if read_error:
        report["warnings"].append({"item": "register", "reason": f"Unable to read register: {read_error}"})
        report["warning_count"] += 1
        report["control_register_complete_for_human_review"] = False

    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Legal-system audit written to {args.output}")
    else:
        print(rendered)
    print(
        f"Controls: {report['resolved_count']}/{report['control_count']} resolved "
        f"({report['approved_count']} approved); {report['blocker_count']} blockers; "
        f"{report['warning_count']} warnings. Release authorised: NO."
    )
    if args.strict and (report["blocker_count"] or report["warning_count"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
