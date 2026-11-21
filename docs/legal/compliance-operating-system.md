# Vocogni Legal & Privacy Compliance Operating System

**Status:** Internal framework draft — not legal clearance and not approved for launch  
**Prepared:** 21 November 2026  
**Scope:** Vocogni learner-facing application, child users, learner records, adaptive learning, third-party providers, and school or pilot deployments.

> **Release rule:** Keep public learner access blocked. This system is a set of governance procedures, evidence registers, technical requirements, and audit tools. It does not establish that any legal requirement has been met. Only the responsible adult operator, qualified Indonesian counsel, and appropriately qualified technical reviewers can approve release evidence for the exact deployed configuration.

## 1. Purpose and system boundary

This document is the control manual for the legal and privacy materials in this folder. It connects:

1. governance and accountable ownership;
2. child-user eligibility, age assurance, and guardian authorisation;
3. lawful purpose, data minimisation, and child-profiling restrictions;
4. notices, consent records, and withdrawal;
5. records of processing and impact assessments;
6. vendor, processor, and international-transfer review;
7. data-subject rights and complaints;
8. retention, deletion, and backup expiry;
9. security incidents and child-safety escalation; and
10. release approval, monitoring, and change control.

The framework applies to the web application, authentication, hosting/runtime, database, optional AI providers, support operations, school integrations, exports, backups, logs, and future features. A new provider, data field, purpose, cohort, or feature requires review before it is enabled.

## 2. Indonesian legal framework to take to counsel

These are primary review sources, not a substitute for advice about the actual operator, service, users, and processing.

| Instrument | Key points for Vocogni | Operating consequence |
|---|---|---|
| [Law No. 27 of 2022 on Personal Data Protection (UU PDP)](https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf) | Lawful basis and transparency; consent evidence; special handling of children's data and guardian consent (Art. 25); high-risk DPIA (Art. 34); security and breach notification (Art. 46); accountability (Art. 47). | Map every purpose to a lawful basis; keep proof; assess high-risk processing before it starts; maintain incident response. |
| [PP No. 17 of 2025 on child protection in electronic systems](https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf) | Child-protection controls, DPIA, privacy-high defaults, parent/guardian consent, a data-protection function, limits on precise geolocation, and restrictions on child profiling (Arts. 7–10 and 19). | Treat child access and child profiling as separate legal gates. Assess exact age band, feature risk, guardian authorisation, best interests, and safeguards. |
| [Permenkomdigi No. 9 of 2026](https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026) | Implements child-protection requirements, including age-band suitability, age verification, and service/feature risk procedures. | Obtain a product- and feature-specific legal assessment of age suitability and the required risk-profile process. Do not invent an internal risk tier and call it an official classification. |
| PP No. 33 of 2026 on implementation of the PDP Law | Promulgated 16 July 2026; Article 225 makes it effective six months after promulgation: **16 January 2027**. It contains detailed consent, child-data, processing-record, retention, breach, DPIA, transfer, and PPDP procedures. | Prepare now. Before 16 January 2027, counsel must check the implementation plan against the effective text and subsequent implementing rules. Do not describe PP 33/2026 as already in force on 21 November 2026. |
| [Permenkominfo No. 5 of 2020](https://jdih.komdigi.go.id/produk_hukum/view/id/759/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Binformatika%2Bnomor%2B5%2Btahun%2B2020) and official [PSE registration guidance](https://pse.komdigi.go.id/panduan/kriteria-pendaftaran-pse-lingkup-privat) | Private electronic-system registration criteria and process. | Indonesian counsel must decide applicability to the actual operator and service, then secure evidence of required registration before relevant operation. |

### Important legal distinctions

- **Guardian authorisation is not the same as learner consent.** A child's click cannot replace required parent/guardian consent.
- **Required child-service authorisation is not an optional feature preference.** PP 17/2025 Article 9 addresses parent/guardian refusal: where required consent is refused, the relevant product, service, or feature must not be provided to the child; the child's consent is void and the child's personal data must be deleted in the circumstances set out there.
- **Optional processing consent is separate.** PP 33/2026 Article 35 (effective 16 January 2027) generally requires the controller to continue providing service without reducing quality when optional consent is refused, except where the processing is necessary to provide the service. Counsel must reconcile this general rule with child-specific refusal consequences under PP 17/2025.
- **Child profiling is a separate restriction.** Under PP 17/2025 Article 19, profiling a child is generally prohibited, with narrowly described exceptions and additional safeguards. A consent checkbox alone does not prove an exception applies.
- **Encryption, local export, session-only processing, or external storage does not itself create a lawful basis or remove child-protection duties.**

## 3. Accountability and roles

The actual data controller/operator must be identified before public release. “Vocogni” is a product name, not necessarily a legal person. The person or entity controlling the purposes and means of processing must be determined by counsel.

| Role | Minimum responsibility | Evidence |
|---|---|---|
| Responsible adult operator / controller | Owns the service, legal accountability, resourcing, decisions, complaints, and release approval. Must have legal authority to operate the service. | Legal identity, authority, address, monitored contacts, signed release decision. |
| PPDP / data-protection function | Advises on obligations, monitors compliance, advises on DPIAs, and acts as a privacy contact where required. PP 17/2025 Article 7 requires a person/function for child-facing PSE; PP 33/2026 Articles 142–146 add appointment conditions and duties. | Appointment, competence evidence, independence/reporting route, contact channel. |
| Qualified Indonesian counsel | Determines legal applicability, lawful bases, age/feature eligibility, profiling exceptions, contracts, transfers, PSE registration, and final notices. | Written advice scoped to exact feature, cohort, operator, date, and legal text. |
| Independent security reviewer | Reviews access control, identity, database isolation, secrets, logs, deletion, incident readiness, and deployment evidence. | Test report, scope, reviewer identity, date, commit/configuration reviewed. |
| Product/engineering owner | Implements approved controls, minimises data, maintains the processing map, and blocks unapproved changes. | Code review, tests, migration records, versioned architecture. |
| Safeguarding contact | Receives child-safety reports and routes them to a responsible adult; does not promise continuous emergency monitoring unless staffed. | Monitored contact, response rota, escalation and closure records. |
| Vendors/processors | Process data only under approved instructions and contracts and report incidents promptly. | Due diligence, contracts, subprocessor list, locations, security and deletion evidence. |

**Minor-maintainer boundary:** A young project maintainer must not be treated as the accountable legal controller, guardian verifier, counsel, or sole safeguarding contact. A responsible adult or properly constituted legal entity must formally own the relevant obligations and approve any real-user operation.

## 4. Processing lifecycle: mandatory gates

### Gate A — Define the service and operator

Before collecting real learner data, record the operator/controller, service description, intended users and age bands, countries, deployment, school involvement, support arrangements, and exact feature scope. Determine whether PSE registration is required.

### Gate B — Maintain the processing register

Use processing-register.template.json as the inventory. For every activity record:
- purpose and lawful basis;
- data categories and data subjects;
- source, system, storage, and recipients;
- processors, transfer destinations, and transfer mechanism;
- access and security controls;
- retention and deletion trigger;
- rights supported; and
- risk and impact-assessment status.

Reconcile the register with actual code, database schema, provider settings, logs, backups, exports, and network requests. A policy draft is not evidence of the live data flow.

### Gate C — Child eligibility and permission

Follow child-access-and-consent-procedure.md. Apply legal age and feature suitability before a child record is created or loaded. Verify required guardian authorisation server-side. Do not rely on self-declared booleans, client storage, email-only assumptions, or a learner's Terms checkbox.

### Gate D — Purpose and profiling

Document a lawful basis for each purpose. Separate necessary service processing from optional features such as external AI, analytics, saved AI history, or additional learning-context sharing. For any processing that may identify, evaluate, or predict aspects of a child, obtain a written Article 19 analysis from counsel and complete the required impact assessment and safeguards before enabling it.

The existing profiling-safeguards policy helper is not a consent collection or verification system. Its evidence inputs are not proof unless supplied by trusted server-side verification. It does not verify guardians, classify age, conduct a DPIA, or integrate a production consent ledger.

### Gate E — Design and security review

Complete the child-specific DPIA before high-risk processing begins. Apply privacy-high defaults, minimum data, least privilege, account isolation, secure secrets, logging redaction, tested deletion, and access controls. If controls cannot be tested, the related feature stays disabled.

### Gate F — Vendor and transfer review

Complete vendor-and-transfer-review.md for every service that receives or can access personal data. Confirm the actual tenant/project region, storage and support locations, subprocessors, contractual role, terms, retention, backup, security, training use (for AI), breach notice, deletion, and cross-border mechanism. Do not infer these details from source code or marketing pages.

### Gate G — Publish accurate notices and collect evidence

Final Indonesian-language notices must identify the real operator and contact, explain purposes, categories, retention, recipients, international transfers, rights, and child safeguards. Consent must be purpose-specific, informed, recorded, and linked to the version of the notice shown before consent. Preserve a proof reference without putting children's personal data or identity documents in Git.

### Gate H — Operate requests and incidents

Follow data-rights-procedure.md, retention-and-deletion.md, and incident-response.md. Use private monitored channels, verify authority proportionately, preserve an audit trail, involve vendors, and meet applicable legal timelines.

### Gate I — Approve and monitor release

A release is blocked until every mandatory control in operational-control-register.template.json has real evidence and launch-readiness.md has been signed by the accountable adult operator, counsel, and security reviewer as applicable. A passing script only validates record completeness. It cannot approve release.

## 5. Current known state — do not overclaim

Repository/source review identifies an Auth0 sign-in flow, Streamlit application runtime, Supabase/PostgreSQL learner-state persistence, Google Fonts browser requests, and a separately gated optional external AI-tutoring path.

The following have **not** been proven by the repository alone:
- the legal identity or authority of the controller/operator;
- deployed region(s), subprocessors, contracts, transfer safeguards, or complete logs/backups;
- age assurance and guardian authority verification;
- a production consent ledger or withdrawal propagation;
- a completed, approved child-specific DPIA;
- a complete, enforced retention and backup-expiry schedule;
- a complete private rights-request and deletion process;
- live database isolation and security testing; or
- final legal notices, PSE decision, and counsel clearance.

The application's existing release gate must remain unchanged and closed for public learner access. Private preview is for restricted synthetic-data operator testing only; it is not a child pilot or a substitute for compliance.

## 6. Required records and storage

| Record | Repository location | Real evidence location |
|---|---|---|
| This operating manual | docs/legal/compliance-operating-system.md | N/A |
| Processing register structure | docs/legal/processing-register.template.json | Adult-controlled private record store |
| Child DPIA | docs/legal/impact-assessment.template.md | Adult-controlled private record store |
| Child-access/consent procedure | docs/legal/child-access-and-consent-procedure.md | Private consent-management system |
| Rights workflow | docs/legal/data-rights-procedure.md | Restricted request case system |
| Incident process | docs/legal/incident-response.md | Restricted incident register |
| Retention/deletion policy | docs/legal/retention-and-deletion.md | Restricted execution log and provider evidence |
| Vendor/transfer review | docs/legal/vendor-and-transfer-review.md | Adult-controlled private contract/evidence store |
| Control register template | docs/legal/operational-control-register.template.json | Private, signed release evidence register |
| Existing release evidence | docs/legal/release-evidence.template.json | Adult-controlled private evidence store |
| Pilot-specific evidence | docs/legal/limited-pilot.template.json | Adult-controlled private evidence store |

Never commit learner names, child/guardian details, ID-document images, signed consent forms, access tokens, private contracts, private evidence URLs, or production screenshots that reveal personal data.

## 7. Change management and review cadence

Internal operating standard (not a statutory deadline):
- review legal sources and the control register at least quarterly;
- review before every new age cohort, school deployment, feature, data category, AI provider, vendor, transfer destination, or purpose;
- review after a security incident, complaint trend, legal change, regulator notice, or material provider change;
- re-run the data map and DPIA where processing or risk changes;
- re-test access, deletion, and release gates for each production deployment; and
- archive exact policy versions, reviewed commit SHA, environment configuration reference, approval date, and expiry/review date.

No feature may ship based only on a completed checklist. The responsible operator records a go/no-go decision for the precise release; counsel and security reviewers record their own scoped decisions.

## 8. Launch decision

**Current decision: NO-GO for public learner-facing use and no processing of real child learner data.**

The framework is a governance and engineering baseline. It is not a substitute for:
1. a responsible adult operator/controller;
2. qualified Indonesian legal advice;
3. a competent child-data protection function;
4. actual consent and age-verification implementation;
5. production infrastructure and vendor verification;
6. DPIA and risk-profile decisions;
7. real operational rights, retention, deletion, and incident processes; and
8. independent release acceptance.

### Primary legal references
- [UU No. 27/2022 — Personal Data Protection](https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf)
- [PP No. 17/2025 — Child Protection in Electronic Systems](https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf)
- [Permenkomdigi No. 9/2026](https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026)
- [PP No. 33/2026 — implementing regulation for UU PDP](https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf)
- [Official PSE registration criteria](https://pse.komdigi.go.id/panduan/kriteria-pendaftaran-pse-lingkup-privat)
