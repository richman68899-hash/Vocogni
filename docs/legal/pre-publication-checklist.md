# Vocogni legal publication checklist

**Status: required pre-launch review.** The draft Terms of Service is not a substitute for a Privacy Notice, child-safety controls, valid consent, or any required registration.

## 1. Fill in the actual operator details

- [ ] Confirm who legally operates Vocogni and who is authorized to accept contracts and complaints on its behalf.
- [ ] Replace all placeholders in `terms-of-service.md`: operator/legal name, address, effective date, support email, privacy contact, rights/content contact, and final Privacy Notice URL.
- [ ] Confirm the operator has legal capacity and authority to run the service and enter user agreements. If the operator/founder is a minor, obtain appropriate adult/legal advice about who must operate the service and accept legal responsibility.
- [ ] Ensure the contact address and email are monitored and can receive complaints and data-subject requests.

## 2. Prepare a separate Privacy Notice before collecting learner data

The current codebase stores authenticated learner state, including profile fields, course progress and attempts, notes, note folders, settings and milestones through the Auth0/Supabase architecture. Confirm this inventory against the deployed version.

- [ ] List every data category, source, purpose, legal basis, recipient/service provider, retention period, deletion schedule and user right.
- [ ] Describe the real hosting/database region and any international transfer only after confirming provider configuration and applicable contracts.
- [ ] Explain how users or parents/guardians can request access, correction, deletion, account closure, or exercise other rights.
- [ ] Document security safeguards, access control, backups, incident response and deletion from backups where applicable.
- [ ] Re-check the Vocogni Assistant data boundary before publication. The current feature specification says its conversation is session-only and it does not send profile/progress data to a third-party hosted model. Any change requires fresh disclosure and legal review.
- [ ] Avoid collecting third-party student/teacher data unless necessary and supported by a lawful basis and required permissions.
- [ ] Make the Privacy Notice accessible before signup and separate any optional consent from acceptance of the Terms.

## 3. Child-data and child-safety requirements

- [ ] Have Indonesian counsel assess application of Law No. 27 of 2022 on Personal Data Protection, including Article 25 on processing children's personal data and parent/guardian consent.
- [ ] Assess the obligations under Government Regulation No. 17 of 2025 on governance of electronic systems for child protection, including whether age assurance, age-based safeguards, risk assessment, or additional operating procedures apply to Vocogni's actual audience and features.
- [ ] Do not onboard under-18 users until the required child-protection safeguards and parent/guardian-consent process are operational, verifiable, and documented.
- [ ] Decide how a parent/guardian provides consent, how Vocogni verifies or records it, how consent can be withdrawn, and how a child account is closed.
- [ ] Keep learner-facing explanations age-appropriate and avoid presenting rule-based practice summaries as validated psychological, clinical, or mastery assessments.

## 4. Electronic-contract and consumer requirements

- [ ] Keep the Indonesian version clear, accessible, and consistent with the actual product. Under Indonesian electronic transaction rules, contracts directed at Indonesian residents have Indonesian-language requirements; obtain counsel review of the final acceptance flow.
- [ ] Add an affirmative, unchecked-by-default Terms acceptance control before account creation/use where appropriate.
- [ ] Keep an audit record of the Terms version, timestamp, account/pseudonymous user ID, and consent event without recording unnecessary sensitive data.
- [ ] Ensure users can reopen the accepted Terms and that a material revision triggers notice and renewed consent when required.
- [ ] Do not use blanket clauses that waive mandatory consumer rights or prohibited liabilities.
- [ ] If billing is ever added, display exact prices, renewal/cancellation terms, and compliant refund terms before purchase.

## 5. Electronic System Operator (PSE) review

- [ ] Ask Indonesian counsel/compliance support whether and how Vocogni must register as a Private Electronic System Operator (PSE Lingkup Privat) with Komdigi/through the applicable OSS process before operating publicly. Official guidance lists several types of private online systems—including services involving offers of goods/services, online communication, content and personal-data processing—as registration criteria.
- [ ] Confirm required service/operator information, responsible contact, reporting and complaint-handling processes, security and operational obligations.
- [ ] Do not claim that Vocogni is registered or compliant until documentation verifies it.

## 6. Launch controls and evidence

- [ ] Remove all bracketed placeholders and verify every statement in the documents against the deployed product.
- [ ] Link Terms and Privacy Notice from the login/signup screen, account/settings area, and any other required access point.
- [ ] Test the full consent, refusal, parent/guardian path, account closure and privacy request path.
- [ ] Save evidence of which legal versions were presented and accepted.
- [ ] Verify no third-party AI provider, analytics service, advertising SDK, or new data recipient has been added without updating disclosures and required consent.
- [ ] Have an Indonesian lawyer review the final Terms, Privacy Notice, child-safety design and consent evidence before public release.

## Official sources for legal review

- [Law No. 27 of 2022 on Personal Data Protection — JDIH Komdigi](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/)
- [Government Regulation No. 71 of 2019 on Electronic Systems and Transactions — JDIH Komdigi](https://jdih.komdigi.go.id/produk_hukum/view/id/695/t/peraturan%2Bpemerintah%2Bnomor%2B71%2Btahun%2B2019)
- [Law No. 1 of 2024 amending the Electronic Information and Transactions Law — JDIH Komdigi](https://jdih.komdigi.go.id/produk_hukum/view/id/884/t/undangundan)
- [Government Regulation No. 17 of 2025 on Child Protection in Electronic Systems — JDIH Komdigi](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025)
- [Private Electronic System Operator (PSE) registration criteria — Komdigi](https://pse.komdigi.go.id/panduan/kriteria-pendaftaran-pse-lingkup-privat)

This checklist is an engineering and document-readiness aid, not a legal determination that each listed rule applies or that the service is compliant. Applicability depends on the operator, product, users, processing activities, and deployment details.