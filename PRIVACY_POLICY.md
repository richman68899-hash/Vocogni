# Vocogni Privacy Policy

**Effective date:** 28 October 2026  
**Version:** Draft 0.1  
**Publication status:** **Draft for review — not approved for public release.**

> **Before publication:** replace the marked controller/contact fields, confirm the actual hosting and data-transfer arrangements, set enforceable retention/deletion procedures, and implement the child-data safeguards in the release checklist. This document describes the current prototype; it does not certify legal compliance.

## 1. Who is responsible for your data?

Vocogni is an educational learning prototype. The person or organisation responsible for deciding why and how personal data is processed must be identified before this notice is published.

- **Responsible operator / data controller:** [INSERT FULL LEGAL NAME OR LEGAL ENTITY]
- **Address:** [INSERT POSTAL OR BUSINESS ADDRESS]
- **Privacy contact:** [INSERT MONITORED PRIVACY EMAIL ADDRESS]

Do not publish this draft while these fields remain incomplete. “Vocogni” is the product name and does not, by itself, identify the legal controller.

## 2. What this notice covers

Vocogni provides course content, lessons, practice questions, learning-progress summaries, notes, folders, milestones, display preferences, and a rule-based learning assistant. This notice explains the personal data the current version may process, the purposes for using it, the service providers involved, and the choices or requests available to users.

The current assistant uses deterministic application logic. It does not currently call a third-party generative-AI model. If the product later introduces an external AI provider or another materially different data use, the notice and relevant choices must be updated before that processing begins.

## 3. What information may be processed?

### Account and sign-in information

When you sign in, the configured authentication flow uses Auth0 and an identity provider. The application receives an identity claim that allows it to associate a signed-in user with their learner record. The provider may supply claims such as your name and email address. Vocogni's saved learner record is keyed by the identity provider's stable subject identifier rather than by your email address.

The authentication and identity providers process information under their own privacy notices and service terms.

### Profile information

Depending on what you enter, your learner profile may include a display name, age, grade, country, learning goals, favourite subjects, perceived strengths and subjects to improve, interests, career interests, learning preferences, preferred difficulty, session length, feedback style, and language preference. Optional profile fields should only be completed when relevant and comfortable to share.

### Learning activity and results

To provide course continuity and progress views, Vocogni may save course selections, lesson completion, diagnostic responses, practice answers, correctness results, scores, question or skill identifiers, mistake tags, timestamps, and related learning-progress records. Diagnostic and progress outputs are prototype learning signals, not official grades, clinical assessments, or validated measures of ability.

### Notes and planning content

If you use Notes or learning milestones, Vocogni may save note titles and content, folder names, folder assignments, milestone titles, end dates, checklists, and completion states. Avoid putting passwords, government identity numbers, financial details, health information, or other highly sensitive information in notes. Do not enter another person's personal data unless you have a proper reason and authority to do so.

### Settings and accessibility preferences

Vocogni may save your theme, font and text-size preferences, background and accent choices, motion settings, feedback timing, hint preference, and related interface options.

### Assistant conversation

The current assistant keeps its conversation in the active Streamlit application session. The current implementation limits the session history to at most 20 message records and displays the latest eight messages in the panel. Assistant conversation history is not included in the durable learner-data bundle written to Supabase. It is not designed to be a permanent chat archive; precise session termination and infrastructure-log retention depend on the platform.

### Technical and service information

The hosting, authentication, database, and browser-resource providers may process technical information needed to deliver, secure, troubleshoot, and operate their services. The exact technical logs and retention periods are controlled in part by those providers and must be checked against the configurations actually used for deployment. Vocogni's current Streamlit configuration disables Streamlit usage-statistics collection, but that setting should not be interpreted as disabling every hosting, security, or infrastructure log.

The interface currently imports font files from Google Fonts. When a browser requests those files, Google may receive connection information associated with that request. This font request is not intended to send your Vocogni notes, profile, or learning-progress record.

## 4. Why we use information

Vocogni uses information only for purposes connected to operating and improving the learning service, such as:

- authenticating the user and associating the session with the correct learner record;
- saving and restoring profile details, learning progress, notes, milestones, and settings;
- presenting course continuity, practice feedback, progress summaries, and rule-based recommendations;
- responding to supported assistant requests using information already available in the learner's current application state;
- protecting the service, diagnosing errors, maintaining system reliability, and handling support or data-rights requests; and
- meeting applicable legal obligations.

Personal data must not be used for an unrelated purpose without a valid legal basis and any notice or consent required by applicable law. The operator must document the lawful basis for each purpose before public release. Depending on the activity and applicable law, that may include providing a service requested by the user, complying with a legal obligation, consent, or another permitted basis. This draft does not substitute for that purpose-by-purpose assessment.

## 5. The assistant, recommendations, and automated outputs

The current Vocogni Assistant uses application rules to answer a limited set of supported requests. When you ask for a summary, recommendation, course list, or explanation of saved practice history, the code may read the relevant profile, progress, notes, milestones, settings, or course catalogue data held in the active application state.

In the current version:

- the assistant does not send learner profile or progress information to an external generative-AI provider;
- the assistant conversation is not written to the durable learner-data bundle;
- requests are not intended to change saved learning records merely by asking a question; and
- recommendations and diagnostic summaries are limited prototype outputs, not professional, clinical, or official academic judgements.

These statements describe the current implementation, not a guarantee about future versions. A future external-model integration must include a fresh data-flow review, appropriate disclosure, any required separate consent, and data minimisation before it is enabled.

## 6. Services that help operate Vocogni

The current architecture uses or may rely on the following providers:

- **Auth0** for authentication: [Auth0 Privacy Policy](https://auth0.com/privacy).
- **The configured identity provider** (for example, Google if enabled in the Auth0 configuration): [Google Privacy Policy](https://policies.google.com/privacy).
- **Supabase** for durable learner-data storage: [Supabase Privacy Policy](https://supabase.com/privacy).
- **Streamlit** for application hosting and runtime: [Streamlit Privacy Policy](https://streamlit.io/privacy-policy).
- **Google Fonts** to deliver interface font files: [Google Privacy Policy](https://policies.google.com/privacy).

These providers process data as needed to provide their services and may separately process service, security, and operational information under their own terms and privacy notices. The operator must confirm the exact providers enabled in production, review applicable provider agreements and subprocessors, and record relevant data flows before release.

Vocogni does not intend to sell personal data or use it for third-party targeted advertising. This does not prevent disclosures to service providers that operate the product, disclosures authorised by the user, or disclosures required by law.

## 7. Where information is stored and international transfers

The current application stores the durable learner-state bundle in a Supabase PostgreSQL table named `learner_progress`. That bundle can contain profile information, course and practice progress, notes, note folders, milestones, and settings. Authentication is handled separately through Auth0 and the configured identity provider.

The actual deployment region of the Supabase project, Auth0 tenant, Streamlit hosting environment, and any relevant subprocessors has not been established by the application code alone. **Vocogni does not make a promise that all personal data remains in Indonesia.** Before launch, the operator must confirm the selected regions and assess any domestic or cross-border transfers against applicable Indonesian requirements and any other law that applies.

## 8. How long information is kept

Vocogni's current prototype does not yet define and enforce a complete, published retention schedule for each category of personal data. Durable learner data may remain in the database until an authorised deletion is carried out. Infrastructure logs and provider backups may follow separate provider retention rules.

Before public release, the operator must set a documented retention period for each category, implement a deletion and backup-expiry procedure where available, and explain any legally required retention exceptions. Data should not be retained indefinitely merely because it is technically convenient to do so.

## 9. Access, correction, deletion, and other data rights

Subject to applicable law and its conditions, you may be entitled to request information about personal data processed about you, obtain access or a copy, correct inaccurate information, request deletion, withdraw consent where processing is based on consent, request restriction or cessation of processing, and exercise other rights available under applicable law.

To make a request, contact the privacy contact listed in Section 1. The operator may need to verify the requester's identity or authority before acting. Requests concerning a child's personal data may require involvement or consent from a parent or legal guardian. Requests will be handled within the time limits required by applicable law.

The current prototype does not yet provide a self-service account deletion control. A verified request may therefore need to be handled by the operator. A documented request workflow and tested deletion procedure are release requirements, not optional enhancements.

## 10. Children's personal data

Vocogni is an educational product and may be relevant to school-age learners. Indonesian Law No. 27 of 2022 on Personal Data Protection treats children's personal data specially and requires parent or guardian consent for its processing. Government Regulation No. 33 of 2026 is scheduled to take effect on 16 January 2027 and adds operational requirements; the operator must verify the applicable requirements and implementation guidance at launch.

**The current prototype does not establish that it identifies child users or obtains and verifies parent/guardian consent. This draft notice is not parental consent and does not fix that product gap. Vocogni must not be publicly launched for children until an appropriate, legally reviewed age-identification, parent/guardian consent and verification, consent-recording, withdrawal, and rights-request process is implemented.**

A parent or guardian who believes that a child's personal data has been provided without the required authorisation should contact the responsible operator using the contact details in Section 1 once those details have been completed.

## 11. Security

Vocogni is designed to use authenticated sessions and server-side database access. The application architecture is intended to keep database credentials out of browser code and source control. These are design intentions, not a representation that the whole service has undergone an independent security audit or that any online service can guarantee absolute security.

Before production release, the operator must verify authentication and account isolation, database access policies, secrets management, backup and recovery, dependency and access reviews, and incident handling. Where applicable law requires notification of a personal-data protection failure, the operator must follow the required deadlines and content of that notice.

## 12. Changes to this policy

This policy should be updated when the product's data practices, providers, purposes, retention rules, or applicable legal requirements materially change. Where required, users must be informed before the change takes effect, and any required new or renewed consent must be obtained separately from general terms and conditions.

The “Effective date” above should be updated whenever a reviewed version is approved for publication.

## 13. Contact

For privacy questions or data-rights requests:

- **Responsible operator:** [INSERT FULL LEGAL NAME OR LEGAL ENTITY]
- **Privacy email:** [INSERT MONITORED PRIVACY EMAIL ADDRESS]
- **Address:** [INSERT POSTAL OR BUSINESS ADDRESS]

These fields must be completed and monitored before this policy is published.

---

## Legal review note

This document is a product-specific draft, not legal advice and not a certification of compliance. It should be reviewed by a qualified Indonesian privacy/legal professional before public launch, particularly because the product may process children's data and uses third-party hosting, authentication, and database services.
