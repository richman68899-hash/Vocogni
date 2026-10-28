# Vocogni Privacy Notice — Working Draft

**Status:** Internal product draft — not approved for public release  
**Prepared:** 28 October 2026  
**Data controller/operator:** Not yet confirmed  
**Privacy contact:** Not yet configured

> **Important:** This is a plain-language product draft, not legal advice and not a finalized privacy policy. The operator must confirm the actual hosting/provider configuration, processing locations, retention periods, lawful bases, child-consent process, rights-request process, and contact details before public release. The current prototype does not have a complete privacy-request or verified guardian-consent workflow.

## 1. What this notice covers

This notice describes the intended handling of information in the current Vocogni development prototype. It should be updated whenever the product, data flow, or provider configuration changes. It is not a claim that the prototype has been independently audited or is compliant with every applicable law.

## 2. Information the current prototype may process

Depending on the features you use, this can include:

- **Sign-in information:** the identity-provider subject identifier and available account claims such as name and email.
- **Learner profile:** information you enter such as grade, age, country, goals, interests, subjects, language preferences, and study preferences.
- **Learning records:** course and lesson progress, diagnostic answers/results, practice attempts, question responses, feedback, and recorded mistake tags.
- **Workspace content:** notes, note titles, learning milestones, and their checklist items.
- **Preferences:** theme, typeface, text size, accent colour, motion, sound, and learning-support settings.
- **Assistant requests:** the current rule-based assistant receives your message and reads the session's available profile, progress, preferences, note and milestone data to produce supported summaries. The conversation is held in the app session; the current assistant does not send its prompt to an external generative-AI provider. Hosting/provider infrastructure may still handle standard technical request information.
- **Technical information:** the app host, identity provider, database, and related services may process operational/security logs under their respective configurations. The operator has not yet documented or independently verified those exact logs and retention windows.

Please do not provide sensitive personal information or information about another person unless it is genuinely necessary and you have the right to share it.

## 3. Why information is used

The intended purposes are to authenticate a learner, restore the learner's own workspace, display progress, provide configured learning features, remember preferences, and diagnose service failures or abuse. Data should not be repurposed for advertising, unrelated profiling, or model training without a separate lawful basis, clear prior notice, and any required consent.

The current assistant uses deterministic request matching and existing app data. It does not make an external generative-AI request. If this changes, the notice must identify the new provider and data flow before launch.

## 4. Where information is stored and who may process it

The repository indicates that:
- an identity provider (currently Auth0 through Streamlit OIDC) handles sign-in;
- Streamlit is used for the app runtime/hosting; and
- Supabase PostgreSQL stores durable learner-state data.

This means information may be processed by these service providers to operate Vocogni. The current operator must still confirm the selected account plans, data-processing terms, storage and processing regions, backup/log retention, subprocessors, access privileges, and any international transfers. This draft does not assert that these details have been fully checked.

The current rule-based assistant does not transmit learner messages to an external generative-AI model. This statement applies only to the implementation reviewed for this draft and must be rechecked after any AI/provider integration.

## 5. Retention, deletion, and account controls

Durable learner data is stored in the existing saved learner-state bundle. The prototype does not yet provide a complete self-service export, correction, account deletion, retention-expiry, or privacy-request workflow. Therefore, the operator cannot yet promise a specific retention period or a fully implemented deletion process.

**This is a release blocker.** Before public use, the operator must define retention by data category, implement and test correction/export/deletion handling, document what backups and provider logs retain, and provide a monitored channel for rights requests.

Until those controls are established, do not store sensitive or essential records in Vocogni, and keep your own copy of important schoolwork.

## 6. Children's data and guardian involvement

Vocogni is an educational prototype that may be used by school-age learners. Under Indonesia's Personal Data Protection Law No. 27 of 2022, Article 25 addresses special handling of children's personal data and parent/guardian consent. Indonesia's child-protection rules for electronic systems also include Government Regulation No. 17 of 2025 and Minister of Communication and Digital Regulation No. 9 of 2026.

The current prototype does **not** verify or record guardian consent and has not completed a documented child-safety risk classification. It must not be treated as cleared for public child use until the operator obtains legal advice on the applicable requirements and implements age-appropriate consent, safety, access, complaint, and risk-mitigation controls.

Official references:
- [Law No. 27 of 2022 on Personal Data Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/)
- [Government Regulation No. 17 of 2025 — Child Protection in Electronic Systems](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025)
- [Minister Regulation No. 9 of 2026 — implementation of PP No. 17 of 2025](https://jdih.komdigi.go.id/produk_hukum/view/id/1007/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Bdigital%2Bnomor%2B9%2Btahun%2B2026)

These references are a starting point for review, not a compliance conclusion.

## 7. Your choices and rights

Subject to applicable law, a learner or authorised parent/guardian may have rights to request information about, access, correction, deletion, objection/withdrawal of consent, or other handling of personal data. The precise rights, response deadlines, identity checks, and any exceptions must be documented by the operator.

At present, Vocogni has no verified in-app privacy-request channel. The operator must add and monitor a contact before public release. No contact address is invented in this draft.

## 8. Security

The application uses authentication and a database, but the complete deployed system has not been independently security-audited. Account isolation, access controls, backups, secrets management, logs, incident response, and deletion must be tested. Do not interpret sign-in or database encryption features as proof that the entire application is secure.

## 9. Changes to this notice

A material change to data categories, purposes, processors, retention, AI provider, or child-safety controls requires an updated notice before the new processing begins and any required additional consent. The operator should preserve version/date history.

## 10. Operator and privacy contact

**Data controller/operator:** not yet confirmed.  
**Privacy contact / rights requests:** not yet configured.  
**Incident-report contact:** not yet configured.

These fields must be completed with real, monitored details before this notice is used as a public policy.
