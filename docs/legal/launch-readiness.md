# Legal and Safety Launch Readiness

Internal release checklist. Do not treat the presence of legal-document drafts as proof of compliance.

## Required before a public launch

- [ ] Insert and verify the responsible operator's legal name and address.
- [ ] Set up monitored general-support, privacy, and safety-reporting contacts.
- [ ] Have qualified counsel review and finalise the Terms of Use, Privacy Notice, and AI Use & Safety Notes for the actual operator and jurisdictions.
- [ ] Obtain qualified legal review of age eligibility, parent/guardian permission and consent, and school deployment responsibilities; implement and test any required verified consent/withdrawal process before processing children's personal data.
- [ ] Assess the service, product, and individual features for applicable Indonesian child-protection requirements, including PP No. 17/2025 and Permenkomdigi No. 9/2026; document minimum-age decisions, age ranges, user verification, risk classification, age-appropriate design, mitigation, complaints/reporting, and review responsibilities. Also assess PP No. 33/2026, which implements the PDP Law and takes effect on 16 January 2027; Article 38 addresses child-user identification, parent/guardian consent, verification using available technology, child-data rights requests, and transition when a user is no longer a child. Qualified Indonesian counsel must determine applicability and implementation. Do not treat this checklist as proof of compliance.
- [ ] Inventory all data fields and purposes against the live application and database schema.
- [ ] Confirm Auth0, Supabase, and hosting provider settings, regions, subprocessors, access controls, backups, logs, and cross-border processing.
- [ ] Set and implement retention, account closure, access/correction/deletion requests, backup removal, and incident response procedures.
- [ ] Determine and complete any applicable Indonesian private electronic system operator registration and other obligations with qualified counsel.
- [ ] Decide whether users must explicitly accept final terms; if so, implement versioned consent records and a clear re-acceptance process. Do not collect a consent acknowledgement against this draft.
- [ ] Keep the restricted private preview separate from a public learner release. The preview requires both VOCogni_INTERNAL_PREVIEW and a server-side VOCogni_INTERNAL_PREVIEW_ALLOWED_SUBJECTS allowlist of exact OIDC sub values; never rely on the preview flag alone. Use synthetic data and restrict the hosting environment.
- [ ] Verify the current source is the code deployed to production and that public statements match that deployment.
- [ ] Confirm the shipped assistant and all AI/data-flow statements match deployed code. The current source has local rule-based commands plus a separate optional external AI-tutoring path that is disabled by default and requires session opt-in. Before enabling that path for real learners, identify the configured provider, review its terms/retention/training/subprocessors/region settings, test the exact data sent, and complete the separate requirements in ai-use-and-safety.md.
- [ ] Verify that users can find the canonical PRIVACY_POLICY.md draft and other policy drafts before sign-in and while signed in. Final notices are not publishable until the controller/contact details are configured and counsel has reviewed them. Decide whether final terms acceptance is required; never record acceptance of a draft as if it were final.
- [ ] Run security, privacy, persistence, account-isolation, accessibility, and mobile UI tests on the actual deployment.

## Current source-based facts

- Authentication is handled through Auth0.
- Learner state is persisted through Supabase/PostgreSQL.
- PR #176 proposes a scoped JSON download of the current Vocogni learner-state bundle. If merged, it will not include external identity-provider records, infrastructure/provider logs, backups, or session-only AI conversation history, and will not replace a full data-rights request workflow.
- The Study Guide has deterministic local commands and a separate optional external AI-tutoring path. The latter is disabled by default, requires a session-only learner opt-in, and sends a bounded subset of chat history plus a limited learning-context summary to the operator-configured provider when used. The actual provider/deployment configuration and its contractual data handling have not been independently verified by this source review.
- The repository review did not confirm a complete self-service account deletion workflow, final data retention schedule, legal operator/contact details, verified guardian-consent process, or completed legal review.
- The in-app privacy notice now renders the root PRIVACY_POLICY.md draft as its canonical source; docs/legal/privacy-notice.md is only an archived pointer to prevent two competing privacy drafts.

Recheck this list whenever the architecture or provider configuration changes.

## Indonesian legal references for launch review

- [Law No. 27 of 2022 — Personal Data Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/) — Article 25 addresses special processing of children's personal data and parent/guardian consent.
- [Government Regulation No. 17 of 2025 — Governance of Electronic System Operators for Child Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025).
- [Minister of Communication and Digital Regulation No. 9 of 2026 — implementing PP No. 17 of 2025](https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026). The regulation took effect on 6 March 2026 and addresses age ranges, child-user verification, product/service/feature risk classification and reassessment, risk mitigation, reporting, and child-friendly design.
- Government Regulation No. 33 of 2026 — implementing regulation for Law No. 27 of 2022 on Personal Data Protection. It was promulgated on 16 July 2026 and takes effect six months later, on 16 January 2027. Article 38 concerns identifying child users, parent/guardian consent and verification, rights requests concerning children's data, and transition out of child status. Verify the enacted text and application with qualified counsel.

These are sources to take to qualified counsel, not a legal opinion or confirmation of compliance.


## Consolidated compliance operating system

Use [the Vocogni Legal & Privacy Compliance Operating System](compliance-operating-system.md) as the central control manual. Complete and maintain its linked records and procedures:

- [Child access, age assurance and guardian authorisation](child-access-and-consent-procedure.md)
- [Processing register template](processing-register.template.json)
- [Child-specific DPIA template](impact-assessment.template.md)
- [Vendor and cross-border transfer review](vendor-and-transfer-review.md) and [vendor register](vendor-transfer-register.template.json)
- [Personal-data rights procedure](data-rights-procedure.md)
- [Retention and deletion policy](retention-and-deletion.md)
- [Incident response procedure](incident-response.md)
- [Operational control register](operational-control-register.template.json)

Run the documentary integrity audit from the repository root:

```bash
python scripts/audit_legal_system.py
python scripts/audit_legal_system.py --strict
```

The strict audit is expected to fail while evidence remains pending. Even a complete audit report does not authorise release. The existing application release gate must remain closed until the responsible adult operator, qualified Indonesian counsel, and independent security reviewer have approved the exact release and the real safeguards have been implemented and tested.
