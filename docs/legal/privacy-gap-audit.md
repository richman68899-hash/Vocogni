# Vocogni privacy and child-safety gap audit

**Audit date:** 19 November 2026  
**Scope:** Repository source and documentation on `main` at base commit `69567ad674461697317885f407360b14a1ebff6f`.  
**Purpose:** Identify the controls that must be completed before a controlled learner soft-launch.  
**Status:** Internal engineering/product audit, not legal advice, an audit of the live deployment, or a compliance certification.

## Executive decision

**Do not soft-launch with real learner accounts or personal learning records yet.** The repository contains a fail-closed learner-access gate and draft notices, but it does not contain a verified age/guardian-consent workflow, a complete data-rights/deletion process, or evidence that actual provider, database, and hosting controls have been reviewed and tested.

A small invited preview using synthetic accounts and synthetic data can be considered only when the preview deployment is actually access-restricted, its exact OIDC subject allowlist is configured, the responsible adult operator accepts the residual technical risk, and no real learner data is collected. The allowlist change proposed in this branch is not active on `main` or the deployed site until it is reviewed, merged, and deliberately deployed.

## Evidence categories

- **Confirmed source gap:** the reviewed repository source does not implement or record the control.
- **Documented but unverified:** the checklist describes the required control, but no evidence proves it is configured or operating.
- **External verification required:** code cannot establish the fact; inspect the live provider, database, contract, dashboard, or deployment.
- **Implemented in this branch only:** the control is proposed in this pull request and is not yet part of the main release.

## Critical blockers — no real-learner soft launch

| Priority | Requirement | Repository evidence / status | Required resolution and acceptance evidence |
|---|---|---|---|
| P0 | **Responsible controller/operator** | The root `PRIVACY_POLICY.md` has placeholders for legal name, address, and privacy contact. Terms have unconfigured operator/support fields. | A responsible adult and appropriate legal person/entity must accept operational responsibility. Record the controller/operator identity and address in the final reviewed notices; do not place private home details or personal contact data in a public repository unless the responsible operator has deliberately approved publication. |
| P0 | **Monitored privacy, support, and safety reporting** | The notices say the channels are not configured. No monitored reporting workflow was established by source review. | Configure monitored channels controlled by the responsible operator; test delivery, ownership, response coverage, escalation, and privacy-request handling. Never direct private data-rights requests to public GitHub issues. |
| P0 | **Age identification and guardian permission** | No verified age assurance, guardian identity verification, consent recording, or consent withdrawal flow was found in the reviewed application. A profile age field and a click-through Terms statement would not establish verified parental consent. | Counsel must first determine the correct age cohort, threshold, assurance method, school/guardian responsibilities, and required legal bases. Then implement a server-verified flow with separate guardian permission, identity/authority verification appropriate to law, purpose and notice version, timestamp, evidence reference, withdrawal, and child-request handling. Test bypass attempts through direct routes, existing sessions, and identity-provider sign-in. |
| P0 | **Child-safety and privacy risk assessment** | The legal checklist calls for age-band, risk classification, feature assessment, and mitigation; no completed assessment or approval evidence was found. | Complete a product/service/feature risk assessment with a qualified adult operator and counsel. Evaluate learner profiling/diagnostics, AI, notes, communications/reporting, and school deployment. Record the scope, risk decisions, mitigations, reviewer, date, and review triggers. Determine whether a DPIA or other formal assessment is required. |
| P0 | **Purposes, lawful bases, and data inventory** | The privacy draft lists broad data categories, but no completed data-flow map, lawful-basis register, or live-schema reconciliation was found. | Map every field and data flow: Auth0 claims, profile, diagnostics, practice attempts, notes, milestones, settings, session chat, technical logs, backups, remote fonts, and enabled providers. For each purpose, document necessity, lawful basis, recipient, access, retention, and children-specific treatment. Remove unnecessary fields and processing. |
| P0 | **Provider contracts, regions, and international transfers** | Auth0, Supabase, Streamlit hosting, Google Fonts, and a configurable AI provider are referenced. The actual tenants, project/hosting regions, subprocessors, agreements, backup locations, access/support routes, and transfer safeguards are not established by source code. | Inspect actual production settings and provider contracts; document the exact entities, processing roles, locations, data received, retention, subprocessors, and safeguards. Confirm whether remote Google Fonts are fetched at runtime. Do not make a data-residency promise without evidence. Keep external AI disabled until its exact provider and data flow are approved. |
| P0 | **Retention schedule and deletion** | No deletion function was found in `persistence.py`; the current privacy draft explicitly says retention is not yet defined/enforced and self-service deletion is absent. | Define retention by data category and trigger, including inactive accounts, requests, logs, provider retention, and backups. Implement a verified request-driven deletion procedure for the Supabase learner record and all associated data; separately handle Auth0 identity, provider logs/backups, and legal exceptions. Test deletion with synthetic records and retain non-sensitive completion evidence. |
| P0 | **Access, correction, withdrawal, and child/guardian requests** | No complete request intake, requester/guardian authority verification, case tracking, or completion workflow was found. | Establish a monitored request channel and a private case workflow with identity/authority verification, deadlines, access/correction/deletion/withdrawal handling, guardian routing, response records, and escalation. Publish only after it is operational. |
| P0 | **Database isolation and privileged-key controls** | `persistence.py` uses server-side Supabase credentials and filters reads/writes by the authenticated OIDC subject. This is useful application-layer isolation, but is not evidence of database-level row security. No SQL migration or RLS policy file was found in the repository tree reviewed. | Inspect the live Supabase grants, RLS status/policies, key type, table exposure, backups, and operator access. Confirm service-role/secret credentials never reach client code or logs. Run two-account tests for read, write, update, session-switch, expired session, and direct API access. Do not treat a source-level `.eq("user_id", ...)` filter as a substitute for verified database controls. |
| P0 | **Incident response and breach handling** | The app notices say there is no live monitoring; no tested incident procedure, ownership/escalation roster, or breach evidence was found. | Establish who monitors reports, how to contain access, disable providers, preserve evidence, assess affected data, contact affected people/guardians, and meet any applicable notification duties. Test the procedure with a tabletop exercise. |
| P0 | **Final notices, terms, and consent records** | `PRIVACY_POLICY.md` and Terms are drafts with placeholders. No final counsel sign-off, published version, or versioned acceptance/consent record was found. | Have counsel review the actual service, controller, data flows, vendors, school/guardian arrangements, and applicable jurisdictions. Publish accurate notices with effective versioning. Where acceptance or consent is the correct basis, record it separately and do not treat a draft notice or general Terms acceptance as guardian consent. |
| P0 | **Release/deployment verification** | Repository CI does not prove the running deployment matches a commit. The existing acceptance checklist explicitly requires a deployed commit identifier and live tests; no such evidence was supplied in this audit. | Record the intended release commit and deployed commit, verify they match, restrict rollback access, and complete real-device/network/auth/data-isolation tests with synthetic data. Keep learner access blocked until sign-off. |

## Important conditional blockers

1. **External AI tutoring:** it is documented as optional, off by default, and session-opt-in. Keep it unavailable for real learners until the provider, contract, data categories, region, retention/training settings, subprocessors, safety testing, incident response, and guardian/legal requirements have been assessed and approved. Session opt-in is not a replacement for legally required guardian consent.
2. **School deployment:** if a school introduces learners, clarify whether the school, Vocogni operator, or another entity makes each processing decision; document roles, notices, instructions, security responsibilities, and permissions before use.
3. **PSE / other operator obligations:** applicability and any registration or other requirements must be determined by qualified Indonesian counsel against the actual service and operator, not guessed from the app's technical stack.
4. **Remote assets and telemetry:** confirm Google Fonts requests, hosting analytics/logs, error reporting, and any future analytics or email SDKs. Re-run the data inventory whenever providers or features change.

## What already exists

- The normal learner path is blocked by `release_gate.py` unless private preview is explicitly enabled.
- `app.py` checks the release gate before initializing/loading learner state.
- The login screen labels Vocogni as a prototype, restricts the stated purpose to invited testers, and tells testers not to enter sensitive or personal information.
- The AI-tutoring path is described as off by default and opt-in for the current session; it should stay off for real learners pending provider review.
- Authenticated persistence uses the OIDC subject as the learner key and filters queries by that subject. This is not a substitute for database-level policy verification.
- Terms, privacy, and AI-safety drafts are available in the application. Draft visibility must not be confused with completed legal notices or consent.

## Changes proposed in the companion pull request

- Require both the private-preview flag and an exact allowlist of OIDC `sub` identifiers. The flag alone no longer authorises any account.
- Re-check the authenticated subject before any learner state is initialised or read; block non-allowlisted accounts and offer sign-out.
- Make the root `PRIVACY_POLICY.md` the single canonical privacy draft shown in-app; retire the older duplicate to avoid policy drift.
- Align the launch checklist and draft notices with PP No. 33 of 2026 and its stated effective date, while retaining PP No. 17 of 2025 and Permenkomdigi No. 9 of 2026 as relevant review references.
- Add regression tests for the preview allowlist, pre-load access gate, canonical in-app privacy source, and the regulatory disclosure.

These changes reduce accidental access and documentation drift. **They do not implement guardian consent, deletion, retention, a DPIA, vendor review, final legal notices, or operational support.**

## Legal review references

The operator and qualified Indonesian counsel should review the enacted text and current implementation guidance for:
- Law No. 27 of 2022 on Personal Data Protection, including Article 25.
- Government Regulation No. 17 of 2025 on child protection in electronic-system operation.
- Minister of Communication and Digital Regulation No. 9 of 2026.
- Government Regulation No. 33 of 2026, including its commencement and Article 38 provisions relevant to child users.

This audit intentionally does not decide which provisions apply to the particular operator or service. That decision depends on the final service design, audience, roles, features, and deployment.

## Sign-off required before learner pilot

- [ ] Responsible adult operator and controller identified.
- [ ] Counsel-reviewed age cohort, child-safety and privacy assessment completed.
- [ ] All required guardian-consent and withdrawal controls implemented and tested.
- [ ] Live provider, transfer, database, RLS, secrets, logging, backup, and retention review completed.
- [ ] Deletion and data-rights request process tested end-to-end.
- [ ] Monitored support/safety/privacy reporting and incident response operational.
- [ ] Final notices and any required acceptance/consent records approved.
- [ ] Exact deployed commit, access restrictions, device tests, and rollback verified.
- [ ] External AI disabled unless separately approved.
- [ ] Responsible adult operator signs the pilot decision and records cohort, data scope, and conditions.

**Release decision: BLOCKED for real learner data until the applicable P0 items are evidenced and signed off.**
