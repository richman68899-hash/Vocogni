"""Documentary evidence audit for a narrow, child-facing Vocogni pilot.

This tool is not legal advice, risk classification, consent verification,
or permission to release the product.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "legal" / "limited-pilot.template.json"
MAX_PILOT_DAYS = 90  # Internal scope-control policy, not a statutory safe harbour.
AGE_BANDS = {"3_5", "6_9", "10_12", "13_15", "16_17"}
PROFILING_DISPOSITIONS = {
    "no_child_profiling", "best_interests_exception",
    "core_feature_actively_requested_by_child", "profiling_disabled_for_pilot",
}
REQUIRED_REVIEWER_ROLE = {
    "adult_operator_and_authority": "responsible_adult_operator",
    "pilot_scope_and_stop_rules": "responsible_adult_operator",
    "age_assurance_and_age_band_assessment": "qualified_indonesian_counsel",
    "ministerial_child_risk_profile": "qualified_indonesian_counsel",
    "article_19_child_profiling_analysis": "qualified_indonesian_counsel",
    "guardian_consent_and_withdrawal": "qualified_indonesian_counsel",
    "child_specific_dpia": "qualified_indonesian_counsel",
    "privacy_by_default_and_age_appropriate_design": "qualified_indonesian_counsel",
    "data_inventory_purposes_and_lawful_basis": "qualified_indonesian_counsel",
    "parental_oversight_and_reporting": "responsible_adult_operator",
    "child_data_protection_contact": "responsible_adult_operator",
    "vendor_contracts_and_cross_border_transfers": "qualified_indonesian_counsel",
    "security_and_account_isolation": "independent_security_reviewer",
    "retention_deletion_and_data_rights": "responsible_adult_operator",
    "incident_response_and_human_monitoring": "responsible_adult_operator",
    "pse_registration_decision": "qualified_indonesian_counsel",
    "deployment_acceptance_and_kill_switch": "independent_security_reviewer",
    "external_ai_provider_review": "qualified_indonesian_counsel",
    "learner_interaction_safety_review": "qualified_indonesian_counsel",
}
NOT_APPLICABLE_ALLOWED = {
    "pse_registration_decision", "external_ai_provider_review",
    "learner_interaction_safety_review",
}


def _date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def _report(blockers: list[dict[str, str]], warnings: list[dict[str, str]],
            approved: int = 0, resolved: int = 0) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": "limited child-facing pilot evidence completeness only",
        "item_count": len(REQUIRED_REVIEWER_ROLE),
        "approved_count": approved,
        "resolved_count": resolved,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "evidence_manifest_complete": not blockers and not warnings,
        "pilot_release_authorized": False,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": [
            "Checks manifest completeness, selected consistency rules, dates, and self-declared reviewer roles only.",
            "Does not verify reviewer identity or qualifications, evidence authenticity, legal sufficiency, guardian consent, or live deployment.",
            "The risk profile must be the actual determination by the competent authority; this script cannot classify a product.",
            "The 90-day limit is internal scope control, not an exemption or statutory safe harbour.",
            "A complete manifest never authorizes access. The responsible adult operator and qualified Indonesian counsel must separately approve the exact release.",
        ],
    }


def validate_manifest(manifest: Any) -> dict[str, Any]:
    """Return blockers and warnings; never grant permission to enable access."""
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def block(item: str, reason: str) -> None:
        blockers.append({"item": item, "reason": reason})

    if not isinstance(manifest, dict):
        for key in REQUIRED_REVIEWER_ROLE:
            block(key, "Manifest must be a JSON object.")
        return _report(blockers, warnings)

    if manifest.get("schema_version") != 1:
        block("schema_version", "Expected schema_version 1.")
    pilot = manifest.get("pilot")
    if not isinstance(pilot, dict):
        pilot = {}
        block("pilot", "Expected a pilot object.")

    for field in ("name", "purpose", "operator_legal_name"):
        value = pilot.get(field)
        if not isinstance(value, str) or not value.strip():
            block(f"pilot.{field}", "A non-empty value is required.")

    commit_sha = pilot.get("release_commit_sha")
    if not isinstance(commit_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit_sha.strip()):
        block("pilot.release_commit_sha", "Record the exact 40-character commit SHA reviewed for the pilot.")

    start, end = _date(pilot.get("start_date")), _date(pilot.get("end_date"))
    if start is None:
        block("pilot.start_date", "Expected a valid ISO date (YYYY-MM-DD).")
    if end is None:
        block("pilot.end_date", "Expected a valid ISO date (YYYY-MM-DD).")
    if start and end:
        duration = (end - start).days
        if duration <= 0:
            block("pilot.end_date", "End date must be after start date.")
        elif duration > MAX_PILOT_DAYS:
            block("pilot.duration", f"Pilot exceeds the internal {MAX_PILOT_DAYS}-day scope limit.")
        if end < date.today():
            block("pilot.end_date", "Pilot end date is in the past.")

    for field in ("participant_limit", "approved_participant_count"):
        value = pilot.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            block(f"pilot.{field}", "Expected a non-negative integer.")
    limit, count = pilot.get("participant_limit"), pilot.get("approved_participant_count")
    if isinstance(limit, int) and not isinstance(limit, bool) and limit <= 0:
        block("pilot.participant_limit", "Participant limit must be greater than zero.")
    if (isinstance(limit, int) and not isinstance(limit, bool)
            and isinstance(count, int) and not isinstance(count, bool) and count > limit):
        block("pilot.approved_participant_count", "Approved participant count exceeds the limit.")

    if pilot.get("recruitment_mode") != "invite_only":
        block("pilot.recruitment_mode", "Recruitment must be invitation-only.")
    if pilot.get("public_signup_enabled") is not False:
        block("pilot.public_signup_enabled", "Public sign-up must be explicitly disabled.")

    age_bands = pilot.get("age_bands")
    if not isinstance(age_bands, list) or not age_bands:
        block("pilot.age_bands", "List the intended age bands.")
        age_bands = []
    else:
        unknown = sorted({str(v) for v in age_bands if not isinstance(v, str) or v not in AGE_BANDS})
        if unknown:
            block("pilot.age_bands", "Unknown age bands: " + ", ".join(unknown))
        if len(set(str(v) for v in age_bands)) != len(age_bands):
            block("pilot.age_bands", "Duplicate age bands are not allowed.")

    features = pilot.get("features_in_scope")
    if not isinstance(features, list) or not features or any(not isinstance(v, str) or not v.strip() for v in features):
        block("pilot.features_in_scope", "List the exact features enabled for participants.")
        features = []

    for field in ("external_ai_tutoring_enabled", "learner_to_learner_interaction_enabled"):
        if not isinstance(pilot.get(field), bool):
            block(f"pilot.{field}", "Set this explicitly to true or false.")
    if pilot.get("external_ai_tutoring_enabled") is False and "external_ai_tutoring" in features:
        block("pilot.features_in_scope", "External AI is in scope while its toggle is false.")
    if pilot.get("external_ai_tutoring_enabled") is True and "external_ai_tutoring" not in features:
        block("pilot.features_in_scope", "External AI is enabled but missing from the feature scope.")
    if pilot.get("learner_to_learner_interaction_enabled") is False and "learner_to_learner_interaction" in features:
        block("pilot.features_in_scope", "Learner interaction is in scope while its toggle is false.")
    if pilot.get("learner_to_learner_interaction_enabled") is True and "learner_to_learner_interaction" not in features:
        block("pilot.features_in_scope", "Learner interaction is enabled but missing from the feature scope.")

    risk = pilot.get("ministerial_risk_profile")
    if risk not in ("low", "high"):
        block("pilot.ministerial_risk_profile", "Record the actual Ministerially determined risk profile; an internal estimate is insufficient.")
    elif risk == "high" and any(band in age_bands for band in ("3_5", "6_9", "10_12", "13_15")):
        block("pilot.ministerial_risk_profile", "High risk does not satisfy the account-eligibility rule for participants under 16.")

    profiling = pilot.get("article_19_profiling_disposition")
    if profiling not in PROFILING_DISPOSITIONS:
        block("pilot.article_19_profiling_disposition", "Record counsel's product-specific Article 19 disposition.")
    elif profiling == "profiling_disabled_for_pilot" and any(
        feature in features for feature in ("adaptive_recommendations", "learner_profile_analytics")
    ):
        block("pilot.article_19_profiling_disposition", "Profiling is marked disabled while adaptive recommendations or learner analytics remain in scope.")

    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
        block("evidence", "Expected an evidence object.")
    for unknown in sorted(set(evidence) - set(REQUIRED_REVIEWER_ROLE)):
        warnings.append({"item": unknown, "reason": "Unknown evidence key; ignored."})

    approved = resolved = 0
    for key, required_role in REQUIRED_REVIEWER_ROLE.items():
        entry = evidence.get(key)
        if not isinstance(entry, dict):
            block(key, "Missing evidence record.")
            continue
        status = entry.get("status")
        if status not in ("pending", "in_review", "approved", "not_applicable"):
            block(key, "Invalid evidence status.")
            continue
        if status in ("pending", "in_review"):
            block(key, "Evidence is not approved.")
            continue
        if status == "not_applicable":
            if key not in NOT_APPLICABLE_ALLOWED:
                block(key, "Not-applicable is prohibited for this child-protection requirement.")
                continue
            if key == "external_ai_provider_review" and pilot.get("external_ai_tutoring_enabled") is not False:
                block(key, "AI review cannot be N/A while external AI is enabled.")
                continue
            if key == "learner_interaction_safety_review" and pilot.get("learner_to_learner_interaction_enabled") is not False:
                block(key, "Interaction review cannot be N/A while learner interaction is enabled.")
                continue

        metadata = ("reviewed_by", "reviewer_role", "reviewed_on", "evidence_ref", "scope")
        missing = [name for name in metadata if not isinstance(entry.get(name), str) or not entry[name].strip()]
        if missing:
            block(key, "Missing review metadata: " + ", ".join(missing))
            continue
        if entry.get("reviewer_role") != required_role:
            block(key, f"Expected reviewer_role '{required_role}'.")
            continue
        reviewed_on = _date(entry.get("reviewed_on"))
        if reviewed_on is None or reviewed_on > date.today():
            block(key, "reviewed_on must be a valid ISO date and cannot be future-dated.")
            continue
        if status == "not_applicable" and (
            not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip()
        ):
            block(key, "Not-applicable requires a written rationale.")
            continue
        if status == "approved":
            approved += 1
            resolved += 1
        else:
            resolved += 1

    return _report(blockers, warnings, approved, resolved)


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
        report["warnings"].append({"item": "manifest", "reason": f"Unable to read manifest: {exc}"})
        report["warning_count"] = len(report["warnings"])
        report["evidence_manifest_complete"] = False
    else:
        report = validate_manifest(manifest)
    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Limited-pilot audit written to {args.output}")
    else:
        print(rendered)
    print(
        f"Pilot evidence: {report['resolved_count']}/{report['item_count']} resolved; "
        f"{report['blocker_count']} blockers; {report['warning_count']} warnings. "
        "Release authorized: no."
    )
    return 1 if args.strict and (report["blocker_count"] or report["warning_count"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
