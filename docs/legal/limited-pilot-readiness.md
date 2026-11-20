# Vocogni — limited, child-facing pilot readiness

**Status:** Internal product/legal analysis for the responsible adult operator and qualified Indonesian counsel.  
**Review date:** 20 November 2026.  
**Scope:** Repository source review, not a live deployment audit.

> This is not legal advice or release approval. "Experimental", "beta", "invite-only", "school pilot", "free", "small cohort", and "not a public launch" do not by themselves create an exemption from laws applicable to the actual service and processing.

## 1. Executive assessment

Vocogni is a child-directed educational learning platform. The current product stores account-linked profile and learning data, produces diagnostics and progress summaries, tracks mistakes and skill performance, and uses these data for recommendations and adaptive learning. Optional AI tutoring can send a learner's prompt, selected prior AI messages, and a limited learning summary to an operator-configured external provider.

**Conclusion:** The product is not inherently unlawful because it is educational or experimental. However, the current repository does not demonstrate the safeguards needed for a real child-facing pilot. Do not enable real child accounts until the responsible adult operator and qualified Indonesian counsel have reviewed the exact pilot and approved its evidence and deployment.

A restricted pilot can reduce exposure and improve supervision. It does not waive child-data or electronic-system obligations.

## 2. What the repository demonstrates

Observed in the source reviewed:
- Auth0 OIDC is used for sign-in; a stable OIDC subject associates a learner with durable data.
- Supabase stores a learner-state JSON bundle. It can contain profile/preferences, age or grade information if entered, learning goals, course progress, practice responses/results, mistakes, notes, milestones, and settings.
- Local Study Guide commands use application logic and saved learner state.
- Optional external AI tutoring is off by default and needs an operator-side feature switch plus a session-only learner opt-in. When enabled, the current request, up to eight selected prior AI messages, and a learning summary can be sent to the configured provider.
- The app expects an elevated server-side Supabase key and scopes database queries to the authenticated subject in application code. Actual key type, project grants, RLS, database region, backups, logs, provider configuration, and production deployment have not been verified from source alone.
- The release gate blocks ordinary learner access. Its private-preview route uses a server-side flag and exact OIDC-subject allowlist and is documented for synthetic test accounts/data.

Not demonstrated as implemented or verified:
- age assurance;
- verified and recorded parent/guardian consent, including refusal, withdrawal, and request handling;
- child-specific DPIA and documented product/feature risk assessment;
- actual Ministerially determined child risk profile;
- counsel-reviewed PP 17/2025 Article 19 child-profiling decision;
- completed privacy-by-default and parental oversight controls;
- child/user reporting channel with monitored safeguarding response;
- final controller/operator identity, address, and monitored privacy/support contact;
- final Terms and Privacy Notice;
- complete retention schedule, account deletion, provider-side deletion, and backup-expiry procedure;
- provider contracts, subprocessors, processing regions, and cross-border transfer analysis;
- independently tested production account isolation and incident response; and
- PSE registration applicability decision and any required registration.

These are source/repository findings, not proof that a live provider setting is absent. The operator must collect deployment evidence.

## 3. Indonesian legal issues for counsel

### A. Children's personal data — Law No. 27 of 2022

Article 25 requires special treatment of children's personal data and parent/guardian consent in accordance with applicable law. Vocogni's account-linked learning records are personal data where they identify or can be linked to a learner. General parental awareness is not the same as a documented, verifiable consent process.

Counsel should settle controller identity, lawful basis for each purpose, age-appropriate notices, guardian authority and verification, recordkeeping, refusal/withdrawal, rights handling, security, retention, breach handling, and processor arrangements.

### B. Child-facing electronic systems — PP No. 17 of 2025

Vocogni is designed for learners and is likely to be accessed by children. PP 17/2025 therefore requires specific analysis of its products, services, and features. Relevant duties include guardian consent, a Personal Data Protection Impact Assessment, high privacy by default, complete and accurate information, age-appropriate functions, partner compliance, and a person responsible for personal-data protection functions.

Article 7(2) prohibits covert practices, collecting precise geolocation from children, and profiling children subject to Article 19 exceptions. The current learning workflow does not appear to need precise geolocation; do not add it.

### C. Child profiling — critical product-design question

Article 19 defines child profiling as processing a child's personal data to identify, evaluate, or predict aspects about the child. The regulation's explanation gives analysis of content preferences from a child's history as an example.

Vocogni's diagnostic scores, course-level accuracy, mistake tags, persistent progress, learning summaries, and adaptive recommendations may fall within this definition. Counsel must classify the actual features; the phrase "learning analytics" does not settle the question.

PP 17/2025 provides exceptions, including strong justification based on the child's best interests and, for default profiling, where profiling is an essential part of the service and actively and consciously requested by the child. Safeguards against harm are required where the child-requested core-feature exception is relied on.

Questions for counsel:
1. Which Vocogni operations are profiling under Article 19?
2. Can each operation satisfy a specific exception, and what evidence supports best interests or an active, conscious request?
3. Does the child understand what is evaluated and how it affects recommendations?
4. Which features must be disabled or redesigned if no exception can be supported?
5. What correction, review, explanation, reset, and deletion controls are required?

A general privacy checkbox or broad "personalised learning" statement is not a substitute for this analysis.

### D. Age bands and risk profile — Permenkomdigi No. 9 of 2026

The regulation applies to products designed for children or likely to be accessed by children. It requires age-band suitability assessment, documentation, age verification, and risk assessment.

Risk assessment includes matters such as contact with strangers, unsuitable content, exploitation, child-data security, addiction, psychological effects, and physiological effects. A high rating on any relevant aspect can result in a high-risk profile; low risk requires all relevant aspects to be rated low under the regulatory framework.

For accounts:
- under 13: only on a child-designed, low-risk product/service/feature, with guardian consent;
- 13 to under 16: only on a low-risk product/service/feature, with guardian consent;
- 16 to under 18: with guardian consent.

The account rule refers to the risk profile determined by the Minister. An internal "low risk" label or this audit's output cannot replace that determination. If Vocogni intends to include learners aged 13–15, official risk classification is a gating issue.

### E. PSE registration and responsible operator

Counsel should determine whether Vocogni is a private electronic system operator within applicable registration categories and complete registration before the relevant operation if required. A small pilot, no-charge access, or invite-only recruitment should not be treated as an automatic exemption without a legal basis.

The responsible legal operator/controller must be identified. The product name alone is not the legal entity. A responsible adult with appropriate authority should own provider contracts, policy approval, consent governance, complaint handling, and release decisions. Counsel should advise on the correct operating structure.

### F. Providers, transfers, and rules effective during the pilot

Auth0, Supabase, hosting, font delivery, and any external AI provider may process information. The operator must map actual providers, data categories, purposes, processor/controller roles, subprocessors, locations, retention, security, and transfers. Do not promise Indonesian data residency unless deployment evidence proves it.

The PDP Law already applies. Counsel should check all implementation rules effective during the proposed pilot. The repository also references PP No. 33 of 2026, scheduled to take effect on 16 January 2027; verify its enacted text and applicability if the pilot continues beyond that date.

## 4. Product-specific risk analysis

| Mechanism | Main issue | Design direction for counsel to assess |
|---|---|---|
| Diagnostic answers, skill scores, mistake tags, adaptive recommendations | Potential child profiling; fairness and learner self-concept | Define purposes and legal exception, minimise retained attributes, make outputs explainable/correctable, remove features that cannot be justified |
| Persistent profile, grade, preferences, notes, progress | Accumulation of account-linked child data | Reduce optional fields, avoid birth dates/identity documents unless strictly necessary, set category-specific retention and rights workflows |
| External AI tutoring | Learner text and learning summary leave Vocogni for a third party | Keep disabled initially unless provider, contract, transfer, training/retention, safety, and consent issues are resolved |
| Streak garden and recurring engagement | Potential addiction or psychological-pressure concern | Avoid punitive streak loss, shame messaging, public rankings, or daily-use pressure; assess age-appropriate defaults |
| AI-generated explanations | Incorrect/inappropriate output; no live moderation in source | Provide monitored adult support, test outputs, show limitations, do not present generated answers as authoritative |
| Supabase persistence with elevated server key | Cross-account exposure if server-side isolation/configuration fails | Independently review least privilege, RLS/grants, query scoping, secrets, logs, backups, and cross-account tests |
| Account sign-in | OIDC login does not establish age or guardian authority | Add proportionate age assurance and verified guardian authorisation after counsel defines lawful methods |

These are product-risk observations, not findings that a feature is unlawful.

## 5. A pilot design to put before counsel

A defensible proposal:
- named, invitation-only cohort; no public self-registration;
- one carefully chosen age band at a time;
- fixed participant cap, dates, and stop conditions;
- responsible adult operator/controller and named child-data protection contact;
- no learner-to-learner messaging or public profiles;
- external AI tutoring disabled initially unless separately approved;
- only data necessary for a declared educational test purpose;
- age assurance and verified guardian consent before relevant child accounts/data processing;
- parent/child reporting and withdrawal route;
- tested account isolation, deletion, retention, incident response, and kill switch; and
- no expansion of ages, participant count, features, providers, or purposes without reassessment.

The 90-day maximum in the companion audit is internal scope control only. It is not a statutory safe harbour and does not reduce legal obligations.

## 6. Evidence audit

The companion JSON template is deliberately all-pending. Create a private working copy in an adult-controlled secure location. Never commit children's names, guardian identity documents, consent forms, participant lists, credentials, or private evidence links to Git.

The script checks manifest structure, evidence status and metadata, reviewer-role labels, dates, pilot scope, cohort limits, invite-only recruitment, official risk-profile declaration, profiling disposition, and selected feature consistency. Reviewer roles are self-declared, not authenticated. The tool cannot verify legal documents, consent records, provider contracts, Ministerial decisions, or the deployed environment.

Run from the repository root:

~~~bash
python scripts/audit_limited_pilot.py
python scripts/audit_limited_pilot.py --strict
python scripts/audit_limited_pilot.py --strict --output artifacts/limited-pilot-audit.json
~~~

It never outputs permission to launch. Keep the existing release gate unchanged while review is pending.

## 7. References for counsel

- Law No. 27 of 2022 — Personal Data Protection Law, especially Article 25: https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/
- PP No. 17 of 2025 — Child Protection in Electronic Systems, especially Articles 5–10 and 18–23: https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf
- Permenkomdigi No. 9 of 2026, especially age-band, risk-assessment, and account-eligibility provisions: https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026
- Permenkominfo No. 5 of 2020 and PSE registration FAQ: https://jdih.komdigi.go.id/produk_hukum/view/id/759/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Binformatika%2Bnomor%2B5%2Btahun%2B2020 and https://pse.komdigi.go.id/pertanyaan-umum

**Bottom line:** Do not replace the current access block with a disclaimer. Obtain written counsel decisions on Article 19 profiling, Ministerial risk profile, age-band eligibility, guardian consent/verification, DPIA, PSE status, and the actual operator/controller. Only then should the responsible adult operator decide whether the exact pilot configuration can be enabled.
