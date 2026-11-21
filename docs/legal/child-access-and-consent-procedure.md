# Child Access, Age Assurance, and Guardian Authorisation Procedure

**Status:** Implementation specification — counsel review required  
**Applies to:** Every feature that may be used by or accessible to a person under 18.

## 1. Non-negotiable decision sequence

Do not create, restore, or expose a child learner record until the applicable legal eligibility and guardian-authorisation gates have passed.

1. Identify whether the user is a child using the counsel-approved, proportionate age-assurance method.
2. Determine the age band and whether the product and each requested feature are suitable for that band.
3. Confirm the product/service/feature risk assessment and any required risk-profile determination.
4. Present the age-appropriate notice and guardian flow.
5. Obtain and verify required parent/guardian authorisation before child access or processing.
6. Record the scope, notice version, timestamp, verification method/reference, expiry or re-verification rule, and current status in a trusted server-side system.
7. Only then allow the specifically authorised product/features to proceed.

The exact method for identifying a user and verifying the guardian must be selected by the responsible operator and qualified Indonesian counsel. Do not collect identity-document images or full birth dates by default. Minimise verification data and delete it when its stated verification purpose is complete, unless a separate legal basis permits retention.

## 2. Age groups and feature eligibility

PP 17/2025 defines a child as a person under 18. Permenkomdigi No. 9/2026 and PP 17/2025 include age-group rules. The documented bands are:

- 3–5
- 6–9
- 10–12
- 13–15
- 16–17 (under 18)

The responsible operator and counsel must specify the minimum age and age-band suitability for each product, service, and feature. Do not assume all bands can use Vocogni. Do not treat an internal “low risk” label as the official risk-profile decision. High-risk classifications and age/account restrictions must be resolved using the enacted rules and counsel's written assessment.

## 3. Guardian authorisation and learner participation

### Required guardian authorisation

For child personal-data processing, the operator must identify the required parent/guardian authorisation and verification process. Under PP 17/2025 Article 9, required guardian consent is obtained before the child may use the product/service/feature. PP 33/2026 Article 38 (effective 16 January 2027) further describes child identification, guardian consent, and verification using available technology.

The consent flow must:
- identify the responsible controller/operator;
- show an age-appropriate explanation of the product and exact data purposes;
- describe what data is collected, why, recipients/providers, retention, rights, and withdrawal route;
- distinguish the guardian's legal authorisation from the child's own understanding and choices;
- verify the guardian relationship/authority with a proportionate, counsel-approved method;
- record notice and policy versions, scope, timestamp, method/reference, result, and status;
- fail closed when required verification cannot be completed; and
- provide a monitored method to withdraw or update permission.

A guardian record must not be represented by a client-supplied boolean, browser local storage, or an unverified email address. The authoritative record and resulting feature permissions must be checked on the server before data access or processing.

### Learner-facing choice

Explain in simple, age-appropriate language what the feature does and how it uses learning activity. Do not use dark patterns, preselected optional choices, forced bundling, confusing wording, or guilt. Where the law requires a child to actively and consciously request a profiling feature, the request must be a distinct, informed action and logged with the feature and notice version.

The child's request does not replace guardian permission where guardian permission is also required.

## 4. Separate permission purposes

Do not bundle these into one “accept all” choice:

| Purpose | Required handling |
|---|---|
| Basic account/service processing | Document its own lawful basis and the specific minimum data required. |
| Guardian authorisation for child use/data processing | Separate verified guardian process; required before access where applicable. |
| Adaptive learning / diagnostics / profiling | Do not enable for children until counsel classifies the exact processing under PP 17/2025 Article 19 and documents an applicable exception, best-interest reasoning, and effective safeguards. |
| External AI tutoring | Off by default; separate, specific choice and provider/transfer review. |
| Sharing prior AI chat history | Separate optional choice, off by default. |
| Sharing learning context with an AI provider | Separate optional choice, off by default. |
| Analytics, marketing, or unrelated secondary purposes | Out of scope unless separately justified, assessed, disclosed, and lawfully authorised. No targeted advertising or commercial learner profiling. |

Refusing optional AI or another optional purpose must not be treated as refusal of required guardian authorisation. Conversely, a storage toggle, local export, or session-only mode must not bypass required guardian permission or child-profiling restrictions.

## 5. Child profiling gate — PP 17/2025 Article 19

Treat the following as potential child profiling until counsel makes a written, feature-specific determination: diagnostic scoring, recurring-mistake labels, learning-skill estimates, learner-level analytics, predicted mastery, personalised pathway selection, and automated evaluation of a child's learning performance.

Article 19 generally prohibits profiling children. It describes limited exceptions, including strong reasons that profiling serves the child's best interests and, for default profiling, an essential/core feature actively and consciously requested by the child. Where relying on the child-requested core-feature exception, the operator must ensure effective technical and operational safeguards against harm.

Before any such processing is enabled:
- counsel documents whether the feature is profiling and the exact exception relied on;
- the responsible operator documents the child's best interests and educational necessity;
- the child's active request is separate from general terms or consent;
- effective safeguards, correction, contest, reset, human review, and deletion are tested;
- the child-specific DPIA and feature risk assessment are approved; and
- the server-side policy gate denies the feature when any required evidence is absent, stale, denied, or withdrawn.

Consent alone does not establish the Article 19 exception. If no exception is supportable, disable or redesign the feature for the affected child cohort.

## 6. Refusal, withdrawal, and invalid permission

- If required guardian consent is refused, missing, invalid, expired under the approved process, or cannot be verified, block the affected child service/features before loading learner data.
- PP 17/2025 Article 9 addresses refusal: the PSE must not provide the relevant product, service, or feature to the child; the child's consent is void and the child's personal data must be deleted in the circumstances specified by the provision. Counsel must determine the complete scope and retention exceptions for the actual product.
- If only optional AI or another optional purpose is refused, keep that optional processing disabled. Continue unrelated service functions where legally permitted and technically separable.
- If consent is withdrawn, immediately revoke future processing permissions, stop outbound provider calls, and execute the approved deletion/restriction process for data whose only lawful basis has ended.
- Do not silently downgrade to an unverified local/session mode to keep a child using a service after a legal refusal.

## 7. Evidence record — minimum fields

The private server-side record should contain:
- pseudonymous learner/account reference;
- age band and age-assurance status, not unnecessary identity documents;
- guardian reference and verification result/method;
- exact notice, policy, and consent versions;
- service and feature scope;
- purposes/data categories authorised;
- affirmative action and timestamp;
- expiry/re-check trigger if required;
- status (pending, granted, denied, withdrawn, expired, invalid);
- withdrawal/refusal event and processing response; and
- audit provenance (server source, event ID, reviewer/system version).

Store evidence in a controlled system. Do not commit records to this repository or expose guardian evidence to course authors, other learners, or ordinary support users.

## 8. Age-out transition

PP 33/2026 Article 38(8), effective 16 January 2027, requires a procedure for transitioning processing mechanisms when a child reaches the age or criteria at which they are no longer treated as a child.

At the transition:
1. re-evaluate age status using the approved process;
2. notify the user in adult-appropriate language;
3. explain current purposes, data categories, providers, rights, retention, and choices;
4. determine whether existing lawful bases and permissions remain valid;
5. obtain any new adult decisions required by law;
6. stop relying on child-only authorisation where it no longer applies; and
7. preserve only necessary audit evidence and complete any required deletion.

Do not silently convert a guardian's approval into unlimited adult consent.

## 9. Acceptance tests before implementation

- Missing age result blocks child access.
- Out-of-scope age band/feature blocks access.
- Missing, unverified, denied, or withdrawn guardian permission blocks access before learner data is loaded.
- Client-side edits cannot grant permission.
- Optional feature refusal leaves that optional feature disabled.
- Child profiling stays disabled until an approved Article 19 decision and all server-verified evidence exist.
- Withdrawal prevents subsequent provider calls and triggers the documented data action.
- Guardian refusal follows the legal child-service consequence, not a storage workaround.
- Rights requests can be made by the child or guardian using the legally approved process.
- Age-out transition re-evaluates notices, lawful basis, and permissions.

## 10. References

- UU PDP No. 27/2022, Articles 21–25: https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf
- PP No. 17/2025, Articles 7–10 and 19: https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf
- Permenkomdigi No. 9/2026: https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026
- PP No. 33/2026, Article 38; effective 16 January 2027: https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
