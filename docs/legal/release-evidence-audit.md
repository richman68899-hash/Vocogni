# Release-evidence audit (engineering helper, not compliance approval)

Vocogni is **not cleared for public learners**. This checklist tool helps a
responsible adult operator and qualified Indonesian counsel track release
evidence. It does not make legal determinations.

## Run

From repository root:

```bash
python scripts/audit_legal_release_evidence.py
python scripts/audit_legal_release_evidence.py --strict
python scripts/audit_legal_release_evidence.py --manifest docs/legal/release-evidence.template.json --strict --output artifacts/legal-release-audit.json
```

The checked-in template intentionally contains only `pending` states. A minor
developer must not self-certify legal/operational requirements. An adult operator
and counsel must review the real evidence. Keep evidence in a secure,
adult-controlled location. Do not store identity documents, guardian details,
private email addresses, secrets, consent evidence, or learner personal data in
this public repository.

## Required review domains

1. Responsible operator/controller identity and operational authority.
2. Final Privacy Notice and Terms.
3. Child-specific product/feature risk assessment and mitigation.
4. Age eligibility and age/user verification.
5. Guardian consent, verification, recording, withdrawal, and refusal handling.
6. Data inventory, purposes, lawful bases, necessity, and minimisation.
7. Actual providers, processor terms, subprocessors, regions, and transfers.
8. Retention, deletion, and backup/provider lifecycle.
9. Data-rights workflow including child/guardian requests.
10. Production access controls, RLS/grants, secrets, and account isolation.
11. Monitored support/reporting and incident-response procedures.
12. PSE registration applicability and required registration/permits.
13. Deployed commit and synthetic-data acceptance.
14. External AI review, or counsel-reviewed non-applicability rationale.

The audit validates statuses, review metadata, ISO dates, scope, and
non-sensitive evidence references. It is not connected to learner access and
cannot authenticate reviewers or validate evidence.

## Legal reference anchors (Indonesia; review with counsel)

- **UU No. 27/2022 (PDP), Article 25:** special processing for children's
  personal data and parent/guardian consent under applicable law.
- **PP No. 17/2025** and **Permenkomdigi No. 9/2026:** child protection
  obligations for electronic systems, including age bands/verification, risk
  assessment, mitigation, reporting and child-friendly design.
- **Private PSE registration:** official Komdigi guidance states providers
  meeting listed criteria must register. Applicability to the actual operator,
  deployment and business structure must be determined by the adult operator
  and counsel.

## Why this PR cannot legally clear Vocogni

The real facts cannot be created by code: legal operator, adult responsibility,
legal review, parent/guardian consent and authority, actual provider contracts
and regions, registration, monitored contacts, and live deployment settings.
A teen developer cannot self-certify these. The learner gate remains active
until responsible adults resolve the real blockers and separately approve
release.
