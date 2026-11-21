# Data Retention, Deletion, and Backup Expiry Policy

**Status:** Policy design draft — retention periods must be set by the adult controller and qualified Indonesian counsel before real learner data is processed.

## 1. Rules

- Keep personal data only for a documented, lawful, necessary purpose.
- Do not use indefinite retention as a default.
- Set a period or objective deletion trigger for every data category.
- Separate active records, security/audit records, support cases, vendor logs, and backups.
- Identify who can authorise deletion and who verifies it.
- Ensure processor agreements provide usable return/deletion and incident-assistance procedures.
- Do not promise immediate deletion from immutable backups or provider logs unless that behaviour is contractually confirmed and tested.
- Preserve only the minimum record required by a documented legal obligation or dispute hold; restrict access and set a review/expiry date.

PP 33/2026 Articles 74–75 require records of processing and a documented retention policy when effective on 16 January 2027. The register must identify the retention period and basis for retaining each data set.

## 2. Retention schedule to complete

The table is deliberately unfilled. The controller and counsel must set the exact period, trigger, and legal basis. Engineering must implement and test the decision.

| Data category | Example location/system | Purpose | Retention trigger / period | Deletion method | Backup/vendor handling | Approval |
|---|---|---|---|---|---|---|
| Auth0 account/identity claims | Auth0 tenant | Authentication | TBD — counsel/operator | Provider-supported account closure/deletion | Confirm provider backups and logs | Pending |
| Learner profile and preferences | Supabase learner_progress JSONB | User-selected profile/service | TBD — counsel/operator | Delete or minimise relevant JSON keys/record | Test restore/backup expiry | Pending |
| Course/lesson progress and answers | Supabase learner state | Course continuity/learning | TBD — counsel/operator | Delete account record or approved scoped data | Confirm backup cycle | Pending |
| Diagnostics, misconception tags, mastery estimates | Supabase learner state | Learning feedback/adaptation | TBD — Article 19 and DPIA review required | Delete/disable derived data and source links | Confirm derived-data deletion | Pending |
| Notes and milestones | Supabase learner state | Learner-created content | TBD — counsel/operator | Delete content and references | Confirm backups | Pending |
| Optional AI messages/context | App session and configured AI vendor | Optional tutoring | TBD — provider contract and counsel | Clear application session; submit provider deletion request if supported/required | Confirm provider logging/training/retention | Pending |
| Consent and guardian-authorisation proof | Future controlled consent service | Demonstrate permissions/accountability | TBD — lawful evidence-retention period | Restrict/delete when no longer necessary or required | Never store identity-document images without approval | Pending |
| Age-assurance evidence | Future verification system/provider | Age eligibility | Delete after verification purpose unless separate lawful retention permits it | Delete underlying verification material; retain minimal status/reference if permitted | Confirm verifier deletion and logs | Pending |
| Security and access logs | Hosting/Auth0/Supabase | Security, abuse prevention, investigations | TBD — provider config and counsel | Provider-supported log expiry/purge | Verify provider retention | Pending |
| Support and rights-request cases | Private operator system | Handle requests/complaints | TBD — legal limitation/claims rules | Restricted purge or anonymisation | Secure case archive/expiry | Pending |
| Incident evidence | Restricted incident system | Response, legal duties, claims | TBD — counsel-approved hold | Secure deletion after hold expires | Preserve only necessary evidence | Pending |
| Backups and snapshots | Supabase/hosting | Recovery | TBD — vendor and recovery policy | Automatic expiry and documented purge process | Test backup lifecycle and restore/deletion reconciliation | Pending |

## 3. Deletion events

The controller must define workflows for:
- verified account-closure request;
- deletion request where legally applicable;
- required guardian-consent refusal and its consequences under PP 17/2025 Article 9;
- withdrawal of a consent-based optional purpose;
- end of the documented purpose or retention period;
- age-band/age-out transition;
- termination of a vendor or school relationship; and
- correction of a record that must not remain in active processing.

For each event, define whether the action is delete, restrict, anonymise, export then delete, or preserve under a documented legal exception. Never decide based solely on engineering convenience.

## 4. Deletion execution checklist

1. Verify requester authority and lawful scope.
2. Identify all systems and processors in the processing register.
3. Stop new collection and processing where required.
4. Export or preserve records only where requested or legally necessary.
5. Delete or correct the live database record.
6. Remove derived learning data and references where they remain personal data.
7. Revoke tokens/sessions and close the account where required.
8. Instruct processors and vendors; capture their confirmation.
9. Record backup expiry and provider-side limitations.
10. Verify that a restore procedure cannot silently reintroduce a deleted learner record.
11. Send a clear completion response, including any unavoidable retention.
12. Restrict and later delete the deletion case record according to its own schedule.

## 5. Architecture requirements

- A delete operation must be idempotent and auditable.
- Account ownership must be established from trusted authentication claims, not a user-supplied ID.
- Deletion must not allow one learner to delete another learner's data.
- Backups and exports must have their own expiry and access controls.
- Any legal hold must be scoped, justified, access-restricted, and reviewed.
- Session-only data must not be described as anonymous if the service can link it to a user or the hosting provider retains it.

## 6. Current status

The repository describes Supabase persistence in learner_progress, but this source review does not establish a complete self-service deletion process, provider-wide purge, backup expiry, or live restore/deletion verification. All schedule entries remain pending until the exact environment and vendor contracts are checked.

## 7. References

- UU PDP No. 27/2022: https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf
- PP No. 17/2025, Article 9: https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf
- PP No. 33/2026, Articles 74–75; effective 16 January 2027: https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
