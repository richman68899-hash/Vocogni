# Vocogni Privacy, Consent, and Learner-Data Architecture

**Status:** Product/legal architecture proposal — not a legal opinion and not approved for deployment  
**Prepared:** 21 November 2026  
**Repository:** richman68899-hash/Vocogni  
**Related documents:** PRIVACY_POLICY.md; docs/legal/privacy-gap-audit.md; docs/legal/limited-pilot-readiness.md; docs/legal/launch-readiness.md; docs/legal/terms-of-service.md; docs/legal/ai-use-and-safety.md

---

## 1. Executive decision

Vocogni should implement a Privacy & Learner Data Architecture (PLDA) that separates four decisions:

1. **Eligibility and authority:** Is this person eligible to use the relevant product, service, and feature, and has any required parent/guardian permission been validly obtained and verified?
2. **Purpose and lawful basis:** For each processing purpose, what lawful basis applies, what information is necessary, and what notice/permission is required?
3. **Personalisation:** May the platform process this learner's performance data to evaluate learning needs and adapt their path?
4. **Persistence and destination:** Is learner data saved to Vocogni's service, held only for the current session, or kept in a genuinely device-only workspace?

Do not combine these decisions into one broad “Accept Terms and Privacy Policy” checkbox.

### Recommended product decision

For the current Streamlit/Auth0/Supabase architecture:

- Keep the existing server-side learner-access release gate.
- Do not use a learner-selected third-party cloud drive as the default privacy alternative.
- Design a **persistent Vocogni profile** and a **session-only, no-durable-learner-record mode** as separate storage choices, but enable either for child users only after counsel confirms the applicable child-protection requirements and the required guardian process is complete.
- Treat true **device-only storage and client-side personalisation** as a later architecture project. A Streamlit application executes Python on a remote server; storing a file in the browser does not make the application's processing local.
- Keep optional external AI tutoring disabled by default and behind a separate, informed choice and provider-specific review.
- Use neutral language defaults. Do not collect gender merely to select grammar or forms of address. Offer an optional preferred form of address, with a neutral default, only if it is demonstrably useful.

**Non-negotiable:** A local-storage or session-only choice must never be used to bypass age rules, required guardian permission, a refusal of required consent, or restrictions on child profiling.

## 2. Why the original proposal needs adjustment

The proposal to offer storage options is useful, but three technical/legal distinctions matter.

### 2.1 Encryption is a security control, not a lawful basis

Encryption can reduce the consequences of unauthorised access. It does not by itself:
- make personal data anonymous;
- remove the data from the scope of data-protection law;
- establish a lawful basis for processing;
- replace parent/guardian permission where required;
- satisfy an age-assurance or child-profiling requirement; or
- remove processor, transfer, retention, or data-rights duties.

If Vocogni stores an encrypted learner record and can later decrypt or associate it with an account, it should continue to treat that record as personal data.

### 2.2 “Local storage” can still involve remote processing

Vocogni currently uses Streamlit as its application runtime. Its Python code, diagnostics, session state, and learner-flow logic execute on the application server. A learner's answer can therefore be processed remotely even if no durable Supabase record is created.

Use accurate product labels:

- **Session-only:** no durable Vocogni learner-progress record is intentionally saved, but the service still processes information during the session and its infrastructure providers may process technical data.
- **Device-only:** learner data and personalisation computations remain on the learner's device; the server does not receive the learner's identifiable answers, profile, or learning history. This is a different architecture and is not what the present Streamlit application provides.
- **Cloud-synced:** learner data is processed by Vocogni's server and saved to its configured database, with the associated processors and transfer arrangements disclosed.

Do not describe a session-only Streamlit mode as “local-only”, “anonymous”, or “no data collection”.

### 2.3 Third-party storage adds another processing relationship

Allowing a learner to select a third-party storage provider may add another recipient, processor/controller relationship, set of terms, security controls, retention rules, subprocessors, and potential cross-border transfers.

For the first release, prefer:
- Vocogni-managed storage with reviewed provider contracts; or
- a learner-controlled export file that they download and manage themselves.

Do not integrate arbitrary external storage destinations until the operator has assessed and documented each provider and its role.

## 3. Indonesian legal issues requiring a written counsel decision

This section is a product-design issue list, not a definitive legal interpretation.

### 3.1 Children's personal data — Law No. 27 of 2022

The Personal Data Protection Law (UU PDP) treats children's personal data as data requiring special handling. Article 25 requires parent/guardian consent for processing children's personal data in accordance with applicable law. The Law also requires processing to be limited, specific, lawful, and transparent, and requires the controller to be able to demonstrate consent where consent is used.

Product implications:
- Identify the actual data controller/operator, not merely the “Vocogni” product name.
- Map each data category to a specific purpose and lawful basis.
- Establish the required child/guardian consent and verification workflow.
- Keep evidence of the applicable notice and permission version.
- Provide routes for access, correction, deletion, and withdrawal where applicable.
- Do not treat the learner's acceptance of Terms as a substitute for required guardian consent.

### 3.2 Child profiling — PP No. 17 of 2025, Article 19

**This is the key legal question for Vocogni's adaptive-learning model.**

Article 19 restricts profiling of children. Its definition covers processing a child's personal data to identify, evaluate, or predict aspects about that child. The regulation provides limited exceptions, including:
- profiling supported by strong reasons that it is in the child's best interests; and
- for default profiling, where profiling is an essential part of the service and the child actively and consciously requests the feature.

Where the child-requested core-feature exception is relied on, effective technical and operational safeguards against harm are required.

Vocogni's diagnostic results, recurring-mistake tags, skill estimates, learner profile, and adaptive recommendations **could** amount to child profiling. This is a legal classification question for qualified Indonesian counsel, based on the real data flow and feature behaviour; this document does not decide it.

Before using those features with children, counsel must provide a written decision on:
1. Which Vocogni features constitute profiling under Article 19.
2. Whether the proposed educational purpose and design can satisfy a specific exception.
3. Whether the profiling is a core feature or optional enhancement.
4. What it means for a child to actively and consciously request that feature.
5. What parent/guardian permission, notices, and evidence are additionally required.
6. What safeguards, review, correction, reset, and deletion controls are necessary.
7. Whether any feature must be disabled or redesigned for a given age/risk cohort.

A generic privacy checkbox, a parent checkbox with no feature explanation, or a Terms clause is not a substitute for this analysis. If no applicable exception is supportable, disable the profiling-dependent feature for the affected child cohort.

### 3.3 Guardian refusal — PP No. 17 of 2025, Article 9

Article 9 addresses the request for parent/guardian consent and the consequence of refusal. It provides that when a parent or guardian refuses the required consent, the electronic-system operator must not provide the relevant product, service, or feature to the child; the child's consent is void and the child's personal data must be deleted in the circumstances specified by the provision.

Therefore, do not tell a child who has been refused required guardian permission that they can simply choose “no cloud storage” and continue with the same child-facing service. A storage toggle is not a workaround for a guardian refusal.

Counsel must determine the precise scope of this requirement for Vocogni's product, features, and age groups. The app should fail closed for any child access that requires permission which has been refused or cannot be validly verified.

### 3.4 Age ranges, age assurance, and risk classification — Permenkomdigi No. 9 of 2026

The regulation sets out age ranges, minimum-age suitability, age verification, self-assessment, and product/service/feature risk-profile processes.

The age bands in PP 17/2025 include 3–5, 6–9, 10–12, 13–15, and 16–under-18. Article 21 sets different account conditions for children in those ranges, including parent/guardian consent and risk-profile conditions. The applicable rules must be assessed for each Vocogni age cohort; an internal “low-risk” label does not replace a formal risk-profile determination where one is required.

Age assurance should be proportionate to the risks and privacy-preserving. The regulation also requires age-verification data to be used for the verification purpose and deleted after that purpose is achieved, unless retention is otherwise permitted by law.

Do not collect identity-document images or full dates of birth by default merely because they are convenient. The operator and counsel should select a proportionate method and document why it is sufficient.

### 3.5 PP No. 33 of 2026 — prepare for 16 January 2027

PP No. 33 of 2026 was promulgated on 16 July 2026 and, under Article 225, comes into force six months after promulgation: **16 January 2027**.

As of this document's preparation date (21 November 2026), that commencement date is in the future. The current PDP Law and child-protection requirements already apply; Vocogni should prepare now for PP 33/2026 rather than treating it as already in force.

Relevant design points include:
- consent information and consent mechanisms should be clear and connected to the relevant notice;
- the controller must be able to demonstrate consent and provide a mechanism to withdraw it;
- Article 35(1) generally says that refusing consent should not reduce service quality, except where the service requires the processing; and
- Article 38 addresses identifying child users, obtaining and verifying parent/guardian consent, and requests concerning a child's data rights.

Article 35 must be read together with the child-specific rules in PP 17/2025, including Article 9. Do not assume the general no-degradation rule overrides the child-specific consequence of a guardian refusing required consent. Obtain counsel's written reconciliation for the actual service and processing purposes.

### 3.6 PSE registration and operating entity

The operator should obtain Indonesian legal advice on:
- the entity/person that is the controller and service operator;
- applicable business registration and KBLI;
- PSE Lingkup Privat registration before relevant use, if required;
- consumer-protection and e-commerce rules if payment is introduced;
- provider contracts and data-processing terms; and
- any sector-specific rules arising from school partnerships.

The official Komdigi PSE guidance identifies the legal framework and categories of private electronic systems requiring registration. The correct answer depends on the operator and actual service, not the app's name.

## 4. Recommended learner-choice model

Do not use one checkbox to bundle storage, adaptive profiling, external AI, analytics, and marketing.

Use a staged flow. The exact age and guardian journey must be set by counsel.

### Stage A — Eligibility and guardian authorisation

Before loading or creating a child learner record:
1. Present the age-appropriate eligibility information.
2. Apply the approved age-assurance method.
3. Determine the relevant age band and feature eligibility.
4. Obtain and verify any required parent/guardian permission.
5. Record the notice version, purpose scope, verification result/reference, date/time, and withdrawal state.
6. If required permission is refused, unavailable, invalid, or withdrawn, block the affected child service/feature and apply the legally required deletion/retention process.

Only collect the minimum information necessary to complete this step. Do not retain guardian identity documents merely as a convenient audit trail; use an appropriate verification provider/reference or other counsel-approved evidence method where possible.

### Stage B — Explain processing purposes separately

After eligibility and required guardian permission have been established, show plain-language, purpose-specific choices.

Proposed purpose categories:

| Purpose | Proposed default | Design rule |
|---|---|---|
| Account, login and basic service security | Necessary processing only | Explain the minimum information and lawful basis. |
| Persistent learner progress | Separate, clear choice where optional | Explain what is saved, why, for how long, and how to remove it. |
| Diagnostic/adaptive learning | Disabled until Article 19 review is complete | Explain what is evaluated, how it changes the learning path, the child-facing safeguards, and the applicable request/permission mechanism. |
| External AI tutoring | Off | Separate opt-in, provider identity, information sent, provider retention/training settings, and transfer details. |
| Product analytics | Off unless separately justified | Prefer aggregated, de-identified operational metrics; do not repurpose child learning records without a lawful basis. |
| Marketing and promotional messages | Off | No bundled marketing permission; no targeted advertising using child profiles. |
| Preferred form of address | Neutral default; optional | Do not infer gender or require gender. Store the least specific preference needed. |

The operator must document the lawful basis for each purpose. A purpose-specific toggle is not automatically “consent” in the legal sense; the UI must reflect the basis selected by counsel.

### Stage C — Choose a permitted storage mode

Offer storage modes only after the user is eligible and required permission is in place.

#### Mode 1: Vocogni cloud-synced learner profile

**Description to the user:** “Save your learning progress to your Vocogni account so you can continue on another device.”

Data may include only the fields needed for the declared learning purposes:
- a pseudonymous account key;
- course and lesson progress;
- attempts and answer results needed for the learning feature;
- limited skill evidence and diagnostic records;
- learner-selected accessibility and learning preferences; and
- notes or milestones only when the learner chooses to use those features.

Controls:
- disclose Auth0, Supabase, hosting and any other actual provider;
- confirm processing roles, regions, subprocessors, retention and transfer safeguards;
- use TLS in transit and provider-supported encryption at rest;
- restrict privileged credentials to server-side use;
- verify account isolation and least privilege;
- enforce and test data deletion and export; and
- apply the approved retention schedule.

This mode is not approved for child users until the controller, guardian process, profiling analysis, security controls and providers have been approved.

#### Mode 2: Session-only, no durable Vocogni learner record

**Description to the user:** “Use this session without saving your learner history to a Vocogni account.”

Potential behaviour:
- keep only the temporary state needed to complete the current session;
- do not create or update a Supabase learner-progress row;
- do not save notes, milestones, profile history, or cross-session diagnostic records;
- clear in-memory learner data at session end or a defined inactivity boundary;
- provide an optional learner-controlled download where lawful and technically safe; and
- explain that hosting, authentication, network, security, and provider logs may still exist.

This mode still performs remote processing in the current Streamlit architecture. It must not be advertised as device-only or anonymous. It is not a workaround for required child permission or a child-profiling restriction.

If a user declines an optional persistence purpose, preserve the rest of the service where legally and technically possible. Do not make optional storage a precondition for unrelated basic course content. If a required processing purpose or child-specific rule prevents use, block only as counsel directs.

#### Mode 3: Device-only learner vault — future release, not current behaviour

**Description to the user:** “Keep your learning record on this device. Vocogni does not receive your saved learner history.”

This requires a different architecture:
- client-side storage such as IndexedDB;
- encryption using well-reviewed browser cryptography;
- a key controlled by the user/device, not sent to Vocogni;
- local calculations for profile-dependent recommendations;
- no transmission of identifiable answer history or learning profile to the server; and
- clear device-loss, export, recovery, and deletion behaviour.

Because Vocogni's present Python/Streamlit code runs on a remote application server, it cannot be called device-only merely by saving a copy in browser storage. A true device-only implementation would require a client-side learning engine or a different frontend architecture.

Do not build custom cryptography. Use established, reviewed platform cryptography and have the design threat-modelled.

### Stage D — Separate external AI permission

External AI should remain a separate feature choice, not bundled with cloud storage or adaptive learning.

Before any real child data is sent to a model provider, document:
- exact provider and legal entity;
- controller/processor roles;
- exact request fields and data categories;
- whether chat history is sent;
- whether learning-profile data is sent;
- data centre and support-access locations;
- retention and deletion settings;
- training use and opt-out status;
- subprocessors and data-transfer safeguards;
- guardian permission and child-facing explanation, if required; and
- a way to disable the feature and stop future transmission.

Default AI context should exclude name, email, account identifier, notes, exact birth date, and unrelated profile information. The current AI safety notice should match the deployed data flow, not an intended future flow.

## 5. Data minimisation and profile redesign

### 5.1 Keep the learning signal, remove unnecessary identity

For adaptive learning, the product may need evidence such as:
- course and skill identifier;
- question identifier;
- correctness and selected response;
- attempt count;
- time or sequence information only if justified;
- diagnostic conclusion and confidence;
- hint/assistance level; and
- revision/retention evidence.

It generally does not need a learner's legal name, personal email, exact date of birth, precise location, gender, or social profile to calculate a next mathematics question.

Keep identity/authentication data separate from learning evidence where practical. Use a pseudonymous internal learner key for course analytics and adaptive computations, with the mapping protected separately.

### 5.2 Gender and pronouns

Do not require a gender selection to use Vocogni and do not infer gender from a name, avatar, voice, or writing style.

If a form of address is genuinely useful, offer:
- neutral default language;
- an optional preferred name or form of address; and
- a way to change or clear that preference.

Do not use gender as an educational diagnostic variable. It has no necessary role in selecting mathematics prerequisites, question difficulty, misconception labels, or mastery status.

### 5.3 Avoid over-collecting age

Use a proportionate age-assurance flow approved by counsel. Keep only the minimum eligibility result or verification reference necessary for ongoing compliance. Where the applicable rule requires deletion of the information used for verification once the purpose is achieved, implement that deletion and test it.

## 6. Consent and evidence records

Consent should be a first-class, auditable workflow, not a Boolean buried in the learner's profile JSON.

The proposed record should capture:

| Field | Purpose |
|---|---|
| Consent event ID | Unique event reference |
| Learner account key | Links the permission to the relevant learner record |
| Guardian verification reference | Evidence that the approved verification process succeeded, without retaining excess documents |
| Guardian role/authority result | Records the type of authority verified |
| Product/service/feature scope | States what the permission covers |
| Purpose identifiers | Separates storage, profiling, AI, analytics, etc. |
| Notice and consent version | Proves what text was shown |
| Choice | Granted, refused, withdrawn, expired, or superseded |
| Timestamp | When the event occurred |
| Verification method and result | Shows how the process was completed |
| Withdrawal timestamp | Records later withdrawal |
| Operator/process version | Supports audit and incident analysis |

Do not store a guardian's ID document image, full ID number, personal address, or phone number in GitHub or in the learner profile. Store only what is strictly necessary for the verified process and legal recordkeeping.

Consent records must be tamper-resistant enough for accountability, access-restricted, and covered by their own retention schedule. A withdrawal must update the access decision and trigger the correct stop-processing/deletion workflow.

## 7. Security architecture requirements

These controls reduce risk; none is a substitute for a lawful basis or required permission.

### 7.1 Authentication and authorization
- Keep Auth0/OIDC separate from Supabase Auth, consistent with the current architecture.
- Derive the learner's internal account key from the authenticated OIDC subject on the server.
- Never trust a browser-supplied user ID to select a database record.
- Verify that every read, write, export and deletion operation belongs to the currently authenticated user.
- Test account switching, logout, expired sessions, direct requests and concurrent sessions.

### 7.2 Database and credentials
- Confirm the exact Supabase key type used in deployment.
- Keep privileged database credentials server-side; never expose them in browser code, logs, commits or public documentation.
- Verify live table grants and RLS policies. A source-code user filter is not evidence of database-level isolation.
- If the application uses a privileged service-role key, remember that it can bypass RLS; RLS alone does not protect against mistakes made by a server process using that key. The server must enforce identity and authorization correctly.
- Use least-privilege roles and test unauthorised access with two synthetic accounts.

### 7.3 Encryption
- Enforce TLS for all network connections.
- Confirm provider encryption at rest and the relevant backup/log encryption coverage.
- Use managed key management and documented rotation/recovery procedures.
- Consider application-level field encryption only where there is a clear threat model and operational key-management plan.
- Do not invent a home-grown cipher or put encryption keys in the same database row as the ciphertext.

### 7.4 Logging and monitoring
- Never log passwords, tokens, guardian documents, full answer histories, notes, or full AI conversations by default.
- Redact or pseudonymise identifiers in operational logs.
- Limit access and retention for logs and backups.
- Monitor security incidents and test the escalation process.
- Ensure the user-facing privacy notice matches what the hosting provider actually logs.

## 8. Terms, Privacy Notice, and consent documents

The repository already contains draft Terms, Privacy Policy and AI safety notices. Keep them separate; they have different functions.

### 8.1 Terms of Use

The final Terms should cover, after counsel review:
1. the correct legal operator and contact details;
2. eligibility, age limits, guardian role and school-use conditions;
3. the educational scope and the fact that practice feedback is not an official school grade or clinical assessment;
4. account and acceptable-use rules;
5. ownership/licensing and permitted use of course content and learner-submitted material;
6. the role and limitations of optional AI;
7. subscription, payment, renewal, cancellation and refund terms if monetisation is introduced;
8. service availability, support, complaints and incident communication;
9. account closure and data-rights routes;
10. changes, effective date, governing law and dispute process; and
11. liability wording that does not attempt to exclude rights or obligations that cannot legally be excluded.

Terms acceptance is not the same as permission to process personal data, and neither is a substitute for a verified guardian-consent record.

### 8.2 Privacy Notice

The final Privacy Notice should describe the actual deployed service:
- controller identity and contact;
- data categories and sources;
- each processing purpose and lawful basis;
- whether each field is required or optional;
- recipients, providers and their roles;
- hosting regions, subprocessors and cross-border transfers;
- retention periods and deletion;
- security controls, limitations and incident contact;
- data-subject rights and response procedures;
- child-specific processing and guardian rights; and
- automated processing/profiling, where applicable, including its purpose and effects.

Do not publish provider or data-residency claims until confirmed against live configuration and contracts.

### 8.3 Child/guardian information and permission

Provide a separate, age-appropriate explanation for the child and a more complete notice for the parent/guardian.

The guardian process should identify the actual feature/purpose being requested, allow a clear refusal, retain evidence of the decision, support withdrawal, and route requests concerning the child's data.

Do not use dark patterns, pre-ticked boxes, forced marketing permission, or bundled optional AI/analytics permission.

### 8.4 Version control

For each final published notice:
- assign a stable version and effective date;
- preserve the exact text shown to each user/guardian;
- record acceptance or permission against the version;
- notify users of material changes as counsel directs; and
- obtain renewed permission where a change requires it.

Never record acceptance against a document that is still marked as a draft.

## 9. Data rights, retention, withdrawal and deletion

Before public release, establish an operator-owned process for:
- access and copy;
- correction;
- withdrawal of consent;
- deletion or termination of processing;
- account closure;
- child/guardian requests;
- export/portability where applicable;
- complaints and escalation; and
- legal exceptions to deletion.

Set a retention schedule by data category, not one indefinite period for the whole account.

A complete deletion process must consider:
1. Supabase learner record and any related rows;
2. Auth0 identity record, where deletion is requested and permitted;
3. external AI provider records, if any were sent;
4. application logs and monitoring systems;
5. backups and replicas, subject to documented technical/legal limits; and
6. copies held by any other processor or recipient.

A download button is useful but does not satisfy all access requests. A database delete alone does not prove that provider logs, backups, or other copies have been handled.

Keep request evidence in a restricted case-management system. Do not use public GitHub issues for personal-data requests or store real learner/guardian evidence in this repository.

## 10. Implementation plan for the current repository

This document is an architecture decision, not an instruction to ship a consent screen before the legal decisions are made.

### Phase 0 — Legal decisions and product classification (blocking)

**Owners:** responsible adult operator, qualified Indonesian counsel, technical lead.

Deliverables:
- named controller/operator and monitored privacy contact;
- age cohort and age-assurance decision;
- applicable Permenkomdigi age and risk profile decision;
- written PP 17/2025 Article 19 profiling determination for diagnostic/adaptive features;
- Article 9 guardian refusal/withdrawal interpretation for the proposed service;
- data-purpose/lawful-basis register;
- DPIA / child-protection risk assessment as required;
- provider, region and international-transfer map;
- PSE and operating-entity applicability decision.

**Gate:** Do not enable real child data or adaptive profiling until the written decisions and required controls are approved.

### Phase 1 — Consent and permission service

Likely files/modules:
- new consent service and tests;
- release_gate.py;
- app.py;
- legal_notices.py;
- new consent/guardian UI components.

Acceptance criteria:
- no learner-data read or write occurs before the required eligibility and permission checks;
- guardian verification is server-validated, not a child-controlled Boolean;
- permission scope and notice version are recorded;
- refusal, expiry, and withdrawal fail closed;
- existing sessions are rechecked when permission status changes;
- a guardian cannot grant consent for an unrelated learner account by changing a browser field;
- no guardian identity documents or real learner records are committed to source control.

### Phase 2 — Storage-mode service

Likely files/modules:
- persistence.py;
- state.py;
- privacy_export.py;
- settings UI;
- new storage-mode tests.

Acceptance criteria:
- cloud-synced mode saves only the approved data categories;
- session-only mode creates or updates no durable learner-progress row;
- switching from cloud-synced to session-only disables subsequent writes and handles previously saved data through the documented retention/deletion rules;
- no local-only claim is made for server-executed Streamlit functionality;
- local export/import is transparent, user-controlled and protected against unsafe file input;
- the chosen mode is respected after refresh, logout and concurrent-session changes.

Do not delete or alter existing learner records as part of a storage-mode migration without an explicit, tested migration and user/guardian notice where required.

### Phase 3 — Adaptive-learning profiling safeguards

Likely files/modules:
- diagnostics.py;
- adaptive_learning.py;
- state.py;
- progress and profile UI;
- tests for recommendations and feature gating.

Acceptance criteria:
- only counsel-approved profiling features can be enabled for the approved age cohort;
- the feature is not active by default where the legal decision requires an active, conscious request;
- the learner receives a clear explanation of what is evaluated and how recommendations change;
- recommendations can be inspected, corrected, reset or disabled where required;
- the system avoids unsupported sensitive inferences;
- a refusal or withdrawal changes the runtime feature decision immediately;
- the system can continue with non-profiled content where that is legally permitted and does not conflict with a child-specific restriction.

### Phase 4 — Vendor, security and rights workflows

Acceptance criteria:
- actual provider entities, regions, subprocessors and contracts are inventoried;
- external AI remains disabled until approved;
- two-account isolation tests pass;
- privileged keys are never present in browser code or logs;
- backup restore and deletion are tested;
- access/correction/deletion/withdrawal requests can be handled within the legal deadlines;
- a breach-response exercise is completed;
- support and safeguarding channels are monitored.

### Phase 5 — Final publication and release approval

Acceptance criteria:
- final Indonesian-language Terms and Privacy Notice are approved by counsel;
- effective versions are published before use;
- consent and acceptance records work as specified;
- the operator/contact fields are complete and monitored;
- applicable PSE registration and business requirements are satisfied;
- the approved age and risk profile is implemented;
- all release-evidence items are complete;
- the existing fail-closed release gate is changed only after written approval and test evidence.

## 11. Required tests

At minimum, write automated tests for these cases before implementing production consent and storage behaviour:

1. Anonymous user cannot read or write learner data.
2. Child user without required guardian permission cannot reach protected learner features.
3. Guardian refusal blocks the relevant child service/feature as counsel determines.
4. Withdrawal immediately revokes the associated feature permission.
5. A child cannot alter a guardian verification result through session state or a browser-supplied field.
6. Consent is tied to the correct learner, purpose, feature, and notice version.
7. Missing or invalid consent records fail closed.
8. Session-only mode performs no durable learner-state database write.
9. Cloud-synced mode preserves existing records and writes only for the authenticated owner.
10. Account switching never displays the previous user's data.
11. External AI receives no request when its feature permission is absent or withdrawn.
12. No sensitive identity or learning data appears in application logs or test output.
13. A deletion request removes the approved data set and records the completion state.
14. A changed privacy notice does not silently inherit old permission where new permission is required.

Use synthetic accounts and synthetic learner data only.

## 12. Release blockers that remain external to code

The following cannot be solved by writing code or adding a Terms clause alone:

- selecting the correct legal operator/controller;
- obtaining qualified Indonesian legal advice;
- determining the child-profiling status and legal exception for adaptive learning;
- obtaining any required official product/feature risk profile;
- deciding the permitted age cohorts;
- validating the parent/guardian verification method;
- signing and reviewing provider agreements;
- confirming actual hosting/database/AI processing locations;
- PSE and business registration determinations;
- approving the final retention and incident-response policies; and
- having an adult with proper legal authority accept the operating obligations.

The founder's age makes the responsible-adult/legal-entity question especially important. A qualified adult operator should control provider contracts, legal notices, consent governance, privacy requests, safeguarding escalation, and release approval.

## 13. Recommended immediate decision

**Approve this architecture for design review only. Do not yet implement a public-facing consent flow or reopen learner access.**

The immediate sequence should be:

1. Ask Indonesian counsel to decide the Article 19 child-profiling question for Vocogni's diagnostics and adaptive recommendations.
2. Confirm the permitted child age cohort and applicable risk profile under PP 17/2025 and Permenkomdigi 9/2026.
3. Confirm how guardian refusal and withdrawal affect access under PP 17/2025 Article 9.
4. Identify the controller/operator and complete the actual provider/data-flow map.
5. Only then implement the permission and storage-mode state machine.

This avoids spending engineering time on a consent interface that cannot legally authorise the proposed processing.

---

## 14. Primary legal references

Use the enacted Indonesian text and obtain counsel's review. Links are provided for source verification, not as a substitute for legal advice.

1. **Law No. 27 of 2022 on Personal Data Protection (UU PDP)** — official JDIH Komdigi:
   https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang%2Bnomor%2B27%2Btahun%2B2022

2. **Government Regulation No. 17 of 2025 (PP 17/2025), Child Protection in Electronic Systems** — official BPK legal database:
   https://peraturan.bpk.go.id/Details/316698/pp-no-17-tahun-2025

3. **Minister of Communication and Digital Regulation No. 9 of 2026 (Permenkomdigi 9/2026)** — official BPK legal database:
   https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026

4. **Government Regulation No. 33 of 2026 (PP 33/2026), implementing the PDP Law** — enacted text; Article 225 sets commencement six months after promulgation on 16 July 2026:
   https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf

5. **PSE Lingkup Privat — official Komdigi FAQ**:
   https://pse.komdigi.go.id/pertanyaan-umum

6. **Minister of Communication and Informatics Regulation No. 5 of 2020 — official JDIH**:
   https://jdih.komdigi.go.id/produk_hukum/view/id/759/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Binformatika%2Bnomor%2B5%2Btahun%2B2020

---

**Document control:** Architecture proposal only. It does not amend the live Privacy Policy or Terms, implement a consent mechanism, establish a lawful basis, certify compliance, or authorise a public or child-facing release.


## 15. Child-learning profiling safeguards: explicit opt-in, fail-closed

### Premise and legal constraint

Profiling is **off by default**. A learner must actively, consciously request the feature after a plain-language explanation of the learning-purpose data categories. Denied, withdrawn, missing, invalid, or expired permission means **no profiling**.

This is a safeguard—not a claim that learner consent alone makes child profiling lawful. PP 17/2025 Article 19 prohibits child profiling, subject to narrowly framed exceptions (including best-interest justification and a core feature actively and consciously requested by the child, with effective safeguards). Vocogni's exact legal route and feature/cohort eligibility must be approved in writing by Indonesian counsel before use. <Cite refs={["turn322841view0"]} />

### 15.1 Learning-purpose data list shown to the learner

The proposed purpose-specific allowlist (legal/learning review required) is:

| Data | Learning purpose | Controls |
|---|---|---|
| Course, lesson, and skill identifiers/progress | Identify the learning objective being practised | Minimal identifiers only |
| Answer outcomes and learner-selected responses | Detect gaps and misconceptions | Scope to relevant questions/objectives |
| Attempts/revisions | Distinguish repeated difficulty from a one-off error | Limited history/window; no indefinite raw event log |
| Course-specific misconception tags | Select an explanation or practice targeting the gap | Neutral wording; never stigmatizing/fixed-ability labels |
| Hint/assistance level | Adjust scaffolding | Record only what is necessary |
| Learner-chosen goals/preferences (e.g. worked examples) | Adapt presentation and next steps | Optional, editable; do not infer sensitive traits |
| Timing/sequence signals (optional) | Evaluate pacing only if validated and necessary | Off by default; separately approved and minimized |
| Provisional mastery estimate/confidence | Select next practice objective | Clearly provisional; explainable, correctable and resettable |

**Excluded from learning profiling:** gender or inferred gender, pronouns, race/ethnicity, religion, precise location, contacts/social graph, ad identifiers, unrelated browsing, health information, family/financial data, private notes, and full external-AI conversation history. No advertising, selling profiles, learner ranking, or unrelated decisions. New data fields require separate necessity, legal, child-safety, and privacy review.

### 15.2 Separate gates: age, guardian, learner, legal and infrastructure

- **Age/cohort:** apply counsel-approved age assurance and age/feature/risk-profile eligibility. Do not treat a self-entered birthdate as legal verification.
- **Guardian:** required guardian permission and authority verification must be completed and server-validated, with purpose/feature/notice scope. The learner cannot set a guardian-verified boolean.
- **Learner request:** child actively and consciously requests profiling; no pre-ticked or bundled consent, no dark patterns.
- **Legal feature approval:** Article 19 exception, child-specific risk assessment/DPIA and safeguard review approved for the feature/cohort.
- **Infrastructure:** live provider, region, subprocessor, contracts, schema/payload/log inventory, access-isolation, secret handling, encryption, retention/deletion/backups, incident-response and request channels reviewed; documented reviewer, evidence version, date and expiry.

If a required permission is refused/withdrawn, profiling stops. Counsel must determine whether the applicable guardian-refusal rule blocks the whole service and triggers deletion; a local/session mode is not a workaround. Age and risk-profile obligations under Permenkomdigi 9/2026 apply to the relevant product/service/features; internal toggles do not prove official eligibility. <Cite refs={["turn322841view0","turn322841view1"]} />

### 15.3 Fail-closed decision matrix

| Learner choice | Verified guardian permission (if required) | Age/cohort + legal feature approval | Infrastructure attestation current | Result |
|---|---|---|---|
| Not asked / no | Any | Any | Any | Profiling off |
| Denied / withdrawn | Any | Any | Any | Profiling off; revoke/reset/deletion/access consequences per counsel |
| Requested | Missing, pending, unverified | Any | Any | Profiling off |
| Requested | Granted and verified | Not approved/unknown | Any | Profiling off |
| Requested | Granted and verified | Approved | Failed/unknown/stale | Profiling off |
| Requested | Granted and verified | Approved | Verified and current | May enable only approved data scope and feature |

Consent evidence and infrastructure approval must be server-controlled, auditable and bound to learner, feature, purpose, notice version, time, expiry/review and withdrawal state. Never accept browser/session/query-parameter claims as proof.

### 15.4 Revocation response

On denial, withdrawal, expiry, or any gate becoming invalid: revoke the decision immediately; prevent profiling reads and writes; cancel queued jobs; invalidate caches; reset/delete profile-derived state as required; and re-evaluate overall child-service eligibility. If guardian refusal requires service termination, block the service—not just profiling. Audit events should contain only pseudonymous account key, purpose/feature scope, consent/verification reference, notice version, timestamp and actor/source. Never include raw learner answers or guardian documents.

### 15.5 Code contract

The proposed pure policy module and tests in this PR are a fail-closed guard only. They do not implement consent collection, age assurance, guardian identity verification, official risk-profile verification, or live infrastructure auditing. Callers must pass server-verified evidence only. The app must remain closed until those systems and evidence are actually implemented and reviewed.
