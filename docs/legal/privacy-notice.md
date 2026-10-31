# Privacy Notice — Prototype Draft

**Status:** Draft for product and legal review. This notice documents the current prototype at a high level; it is not a finding that the service complies with every applicable privacy requirement.

- **Responsible data controller/operator:** NOT CONFIGURED — identify the responsible data controller/operator and address before public launch
- **Privacy contact:** NOT CONFIGURED — add a monitored privacy contact before public launch
- **Effective date:** NOT SET — publish an effective date only after legal review
- **Version:** 0.2-draft

## 1. Information the prototype may process

Depending on how you use Vocogni and how the deployment is configured, the service may process:

- **Account and authentication information** needed to sign in, such as a name or email address provided through the authentication flow.
- **Profile and preference information** you choose to enter, such as grade, learning goals, preferred language, or display settings.
- **Learning records** such as selected courses, lesson progress, diagnostic answers, practice attempts, scores, and mistake tags.
- **Workspace content** such as notes, folder names, milestone titles, and checklist items you create.
- **Assistant conversation content** that you type into the Study Guide.
- **Technical and operational information** processed by the app host, authentication provider, or database provider to provide and secure their services.

Avoid entering sensitive personal information unless the service specifically asks for it and the operator has explained the lawful purpose and handling.

## 2. Why the information is used

The prototype uses this information to authenticate a learner, restore saved state, display progress, provide supported rule-based learning recommendations, show the learner's notes and settings, and maintain and troubleshoot the application.

If the learner explicitly enables optional AI tutoring for the current session, the service also uses the current assistant message, up to eight messages from prior AI-tutoring turns; local profile, progress, and notes summaries are excluded from chat history, and a limited learning-context summary to generate a response. The summary may include grade level, selected learning preferences, course-level practice accuracy, and recorded mistake tags. The application does not add the learner's name, email, account ID, saved notes, milestones, age, or country to this summary. A learner can still type personal information into a message; users should not do so.

The operator should map every deployed data field and provider to a documented purpose before public launch, and should not collect information merely because it might be useful in the future.

## 3. Where information is processed

- **Auth0** is used for authentication.
- **Supabase/PostgreSQL** is used to persist learner state.
- The application runs on a hosting platform; the exact deployment configuration and associated technical logs must be documented by the operator.
- **Optional AI provider:** when AI tutoring is enabled and configured, assistant inputs and the limited learning summary are sent to the external provider configured through the application's server-side settings. The provider name and processing location depend on the operator's configuration and must be identified before public use.

The operator must confirm provider terms, data regions, access controls, backups, subprocessors, retention periods, and any cross-border transfers for the actual deployment. Do not assume that all processing occurs in Indonesia.

## 4. The Study Guide and AI processing

Local Study Guide commands use application code and saved Vocogni data. They do not require an external generative AI request.

Open-ended AI tutoring is optional and off by default. The learner must enable a session-only opt-in control before an unhandled open-ended request is sent to the configured provider. If no provider is configured, the AI option is unavailable and local commands remain usable.

The LLM integration uses an OpenAI-compatible Chat Completions API. The server sends the current message, up to eight recent chat messages, and the limited learning-context summary described above. The provider's own terms, retention, training use, subprocessors, security controls, and processing locations govern its handling of those inputs. Vocogni does not promise that provider inputs are never retained or never used for model improvement.

This prototype's opt-in control does not verify or record parent/guardian consent and does not by itself satisfy any legal consent requirement.

## 5. Sharing and disclosure

The current architecture necessarily relies on its authentication, database, and hosting providers to operate. When AI tutoring is enabled, the configured AI provider also processes the assistant inputs described in Section 4. The final notice must identify the actual providers and explain their roles and any other sharing that occurs. The operator should not promise that information is never shared or never leaves a country unless the deployed configuration and contracts support that promise.

## 6. Security and retention

The operator should apply appropriate access controls, keep credentials and secrets out of source code, limit internal access, and maintain a process for handling incidents. No internet service can promise absolute security.

Learner-state persistence is implemented in Supabase, but the retention schedule, backup-deletion timeline, and user-facing account/data deletion process have not yet been finalised for this prototype. These must be decided, implemented, and described before public release. Until then, do not promise a specific deletion deadline.

## 7. Your choices and data rights

The learner can leave AI tutoring disabled and continue using local Study Guide commands. The session opt-in is not persisted as a long-term preference. Depending on applicable law and the actual deployment, users may have rights to request information about processing, access a copy of their data, correct it, request deletion or restriction, or withdraw consent where consent is the relevant legal basis.

The service must provide a working channel to make these requests and a documented process for responding. **Privacy contact: not configured.** A monitored privacy contact and request-handling process must be in place before public launch. The operator must also confirm how requests from parents/guardians and school administrators are handled without disclosing another learner's information.

## 8. Children and school use

The service is intended for learning, and learners may be minors. Article 25 of Indonesia's Personal Data Protection Law (Law No. 27 of 2022) provides for special handling of children's personal data and requires parent/guardian consent in accordance with applicable law. Indonesia also has electronic-system child-protection rules, including Government Regulation No. 17 of 2025 and Minister of Communication and Digital Regulation No. 9 of 2026. Their exact application to Vocogni must be assessed by qualified counsel against the service's role, features, user groups, deployment, and risk classification.

The current prototype does not verify or record parent/guardian consent and has no documented child-safety risk classification. Do not treat this draft or the login screen as satisfying consent or compliance requirements. Public child-facing use should remain blocked until the operator completes the legal assessment and implements the controls that assessment requires.

## 9. Changes to this notice

The published notice should show an effective date and version. Material changes in collected data, providers, AI processing, purposes, or retention should trigger an appropriate update and user communication before the changed processing begins, where required.

## 10. Legal reference for launch review

For Indonesia, have qualified counsel review the actual service and deployment against the laws and regulations that apply. The references below are a starting point for review, not a legal conclusion about applicability or compliance.

- [Law No. 27 of 2022 — Personal Data Protection, Ministry JDIH](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/). Article 25 addresses special handling of children's personal data and parent/guardian consent.
- [Government Regulation No. 17 of 2025 — Governance of Electronic System Operators for Child Protection, Ministry JDIH](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025).
- [Minister of Communication and Digital Regulation No. 9 of 2026 — implementing PP No. 17 of 2025, Ministry JDIH](https://jdih.komdigi.go.id/produk_hukum/view/id/1007/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Bdigital%2Bnomor%2B9%2Btahun%2B2026). The official abstract covers, among other matters, product/service/feature risk profiles, self-assessment and verification, risk mitigation, reporting/complaints, and child-friendly design.
- [Government Regulation No. 71 of 2019 — BPK regulatory database](https://peraturan.bpk.go.id/Details/122030/pp-no-71-tahun-2019).
- [Ministerial Regulation No. 5 of 2020 — private electronic system operators, Ministry JDIH](https://jdih.komdigi.go.id/produk_hukum/view/id/759/t/pera). Counsel should confirm current status and applicability, including any subsequent amendments or replacement rules.
