# Legal and Safety Launch Readiness

Internal release checklist. Do not treat the presence of legal-document drafts as proof of compliance.

## Required before a public launch

- [ ] Insert and verify the responsible operator's legal name and address.
- [ ] Set up monitored general-support, privacy, and safety-reporting contacts.
- [ ] Have qualified counsel review and finalise the Terms of Use and Privacy Notice for the actual operator and jurisdictions.
- [ ] Confirm age eligibility and parent/guardian permissions for users under 18; define school deployment responsibilities.
- [ ] Inventory all data fields and purposes against the live application and database schema.
- [ ] Confirm Auth0, Supabase, and hosting provider settings, regions, subprocessors, access controls, backups, logs, and cross-border processing.
- [ ] Set and implement retention, account closure, access/correction/deletion requests, backup removal, and incident response procedures.
- [ ] Determine and complete any applicable Indonesian private electronic system operator registration and other obligations with qualified counsel.
- [ ] Decide whether users must explicitly accept final terms; if so, implement versioned consent records and a clear re-acceptance process. Do not collect a consent acknowledgement against this draft.
- [ ] Verify the current source is the code deployed to production and that public statements match that deployment.
- [ ] If adding generative AI, complete the separate requirements in ai-use-and-safety.md before enabling it.
- [ ] Run security, privacy, persistence, account-isolation, accessibility, and mobile UI tests on the actual deployment.

## Current source-based facts

- Authentication is handled through Auth0.
- Learner state is persisted through Supabase/PostgreSQL.
- The current Vocogni Assistant is rule-based and does not call an external generative AI model.
- The repository review did not confirm a complete self-service account deletion workflow, final data retention schedule, legal operator/contact details, or legal review.

Recheck this list whenever the architecture or provider configuration changes.
