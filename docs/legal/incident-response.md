# Personal-Data and Child-Safety Incident Response Procedure

**Status:** Operational draft — must be staffed, tested, and approved before real learner data is processed.  
**Priority:** Protect learners first; preserve evidence; involve the responsible adult operator and counsel immediately.

## 1. What counts as an incident

Escalate suspected or confirmed events affecting confidentiality, integrity, or availability of personal data, including:
- another learner's record being visible or modified;
- exposed credentials, tokens, database keys, or backups;
- unauthorised account access or data export;
- lost, altered, disclosed, or inaccessible learner data;
- a processor or AI vendor reporting an incident;
- a public/private dataset or repository containing real child data; or
- a child-safety event involving disclosure, abuse, coercion, harmful contact, or unsafe output.

A report does not need to be proven before escalation. Do not ask a learner to investigate or gather evidence.

## 2. Immediate actions

1. **Receive and protect:** move the report to a private channel; do not reproduce sensitive material in a public issue.
2. **Notify the adult incident lead:** the responsible adult operator and PPDP/privacy contact must be reachable. If no adult incident lead is staffed, real-user access must remain disabled.
3. **Contain safely:** disable the affected feature, revoke exposed credentials, restrict affected accounts/keys, stop outbound AI/vendor transfers where needed, and preserve required evidence. Do not destroy logs or evidence.
4. **Scope:** identify affected systems, data categories, people/age groups, recipients, time window, and possible onward transfers.
5. **Assess:** evaluate risk to learners, including potential identity exposure, account compromise, educational harm, profiling misuse, and child-safety consequences.
6. **Involve processors:** require vendors to notify the controller promptly and cooperate with investigation, containment, restoration, and deletion.
7. **Document:** record detection, when the event became known, actions, decisions, notifications, and recovery.
8. **Recover:** restore from verified clean sources, rotate secrets, test account isolation, and monitor for recurrence.
9. **Review:** identify the root cause, required safeguards, linked DPIA/register entries, and whether the feature must remain disabled.

## 3. Statutory notification clock

Under UU PDP Article 46, the controller must provide written notice within **3 × 24 hours** to the affected data subject and the relevant institution in the circumstances covered by that provision. PP 33/2026 Article 114 (effective 16 January 2027) specifies that its clock runs from when the personal-data protection failure is known with certainty, reasonably and properly, and requires at least:
- the personal data disclosed/affected;
- when and how the failure occurred;
- handling and recovery steps; and
- information about the PPDP or designated contact.

Do not wait for the full forensic investigation before escalating the notification decision. The adult operator and counsel must determine whether the legal threshold is met, which recipients must be notified, and the applicable current authority/contact procedure. Do not invent or assume a regulator portal/contact.

PP 33/2026 Article 115 also addresses public notification in specified serious/public-service circumstances. Counsel must assess that duty separately.

## 4. Notification preparation

A written notice, when legally required, should be accurate and understandable and include:
- what happened and when it was discovered;
- data categories and affected services;
- what is known and what remains under investigation;
- likely consequences and relevant child-specific risks;
- containment, mitigation, and recovery steps;
- practical protective steps for the affected person;
- contact details for the PPDP/privacy contact; and
- when further updates will be provided.

Do not disclose another affected learner's identity. Avoid unsupported reassurance or speculation.

## 5. Incident log fields

Store a restricted record:
- incident ID and severity;
- first report, detection, and confirmed-knowledge timestamps;
- reporter channel and triage lead;
- affected product/features, systems, vendors, and commits/configuration;
- affected data categories and estimated subjects/cohorts;
- confidentiality/integrity/availability impact;
- containment and credential-rotation steps;
- counsel/PPDP/operator decisions and reasons;
- notification recipients, content, and timestamps;
- processor reports and evidence;
- recovery checks and learner support actions;
- root cause and preventive actions;
- linked DPIA, processing-register, and release-control updates.

Do not put learner names, guardian details, raw records, tokens, or confidential evidence in GitHub.

## 6. Severity and stop conditions

Treat confirmed cross-account access, exposed child records, unauthorised child profiling, exposed identity documents, or an unreviewed provider receiving child data as critical. Disable the affected data flow immediately, preserve evidence, and escalate to the adult operator/counsel.

Do not reopen a feature until:
- the scope is known well enough to make a safe decision;
- access controls and data flows have been corrected;
- incident and rights obligations have been assessed;
- affected people have been dealt with as legally required;
- security tests have passed; and
- the operator, counsel, and security reviewer have documented re-approval.

## 7. Tabletop test

Before any pilot, run a synthetic-data tabletop exercise for:
1. a learner viewing another learner's progress;
2. a database credential being exposed;
3. an AI provider receiving a message after opt-out;
4. a processor reporting a breach; and
5. a guardian refusing or withdrawing required permission.

Record detection time, responsible adult contact, containment decision, legal notification analysis, communications, deletion, and restart approval. Do not use real child data in the exercise.

## 8. References

- UU PDP No. 27/2022, Article 46: https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf
- PP No. 33/2026, Articles 114–118; effective 16 January 2027: https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
