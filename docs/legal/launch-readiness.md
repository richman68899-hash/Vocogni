# Legal and Safety Launch Readiness

Internal release checklist. Do not treat the presence of legal-document drafts as proof of compliance.

## Required before a public launch

- [ ] Insert and verify the responsible operator's legal name and address.
- [ ] Set up monitored general-support, privacy, and safety-reporting contacts.
- [ ] Have qualified counsel review and finalise the Terms of Use, Privacy Notice, and AI Use & Safety Notes for the actual operator and jurisdictions.
- [ ] Obtain qualified legal review of age eligibility, parent/guardian permission and consent, and school deployment responsibilities; implement and test any required verified consent/withdrawal process before processing children's personal data.
- [ ] Assess the service, product, and individual features for applicable Indonesian child-protection requirements, including PP No. 17/2025 and Permenkomdigi No. 9/2026; document minimum-age decisions, risk classification, age-appropriate design, risk mitigation, complaint/reporting, and review responsibilities. Do not treat these checklist items as proof that a particular legal duty applies or has been satisfied.
- [ ] Inventory all data fields and purposes against the live application and database schema.
- [ ] Confirm Auth0, Supabase, and hosting provider settings, regions, subprocessors, access controls, backups, logs, and cross-border processing.
- [ ] Set and implement retention, account closure, access/correction/deletion requests, backup removal, and incident response procedures.
- [ ] Determine and complete any applicable Indonesian private electronic system operator registration and other obligations with qualified counsel.
- [ ] Decide whether users must explicitly accept final terms; if so, implement versioned consent records and a clear re-acceptance process. Do not collect a consent acknowledgement against this draft.
- [ ] Verify the current source is the code deployed to production and that public statements match that deployment.
- [ ] Confirm the shipped assistant and all AI/data-flow statements match deployed code. If adding generative AI, complete the separate requirements in ai-use-and-safety.md before enabling it.
- [ ] Verify that users can find the policies before sign-in and while signed in, and decide whether final terms acceptance is required. Never record acceptance of draft notices as if they were final.
- [ ] Run security, privacy, persistence, account-isolation, accessibility, and mobile UI tests on the actual deployment.

## Current source-based facts

- Authentication is handled through Auth0.
- Learner state is persisted through Supabase/PostgreSQL.
- The current Vocogni Assistant is rule-based and does not call an external generative AI model.
- The repository review did not confirm a complete self-service account deletion workflow, final data retention schedule, legal operator/contact details, or legal review.

Recheck this list whenever the architecture or provider configuration changes.

## Official Indonesian child-protection references for legal review

- [Law No. 27 of 2022 — Personal Data Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/) — Article 25 addresses special processing of children's personal data and parent/guardian consent.
- [Government Regulation No. 17 of 2025 — Governance of Electronic System Operators for Child Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025).
- [Minister of Communication and Digital Regulation No. 9 of 2026 — implementing PP No. 17 of 2025](https://jdih.komdigi.go.id/produk_hukum/view/id/1007/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Bdigital%2Bnomor%2B9%2Btahun%2B2026). The official abstract addresses product/service/feature risk profiles, age limits, risk mitigation, reporting/complaints, and child-friendly design.

These are sources to take to qualified counsel, not a legal opinion or confirmation of compliance.
