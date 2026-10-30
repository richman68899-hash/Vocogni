# Vocogni legal launch checklist

**Review date:** 28 October 2026  
**Status:** Pre-launch work required. This checklist is operational guidance, not a legal opinion.

The Terms of Service and in-app Terms page have been drafted, but they are **not publication-ready**. Do not describe this change as making Vocogni legally compliant. A terms document does not replace consent records, a Privacy Notice, age-assurance controls, risk assessments, incident processes, or counsel review.

## Release blockers

- [ ] **Identify the operator.** Confirm the full legal name of the party operating Vocogni, legal/business address, applicable registration details, and a monitored support/privacy contact. Replace every bracketed placeholder in TERMS_OF_SERVICE.md.
- [ ] **Obtain Indonesian legal review.** Review the final Terms, consumer-facing language, limitations of liability, data handling, and any planned payment terms.
- [ ] **Publish a separate Privacy Notice before public use.** It should accurately specify the data controller, categories of data, purposes, lawful bases, collection sources, processors/recipients, transfers and hosting locations, retention/deletion, security, breach handling, data-subject rights, and a working request channel.
- [ ] **Map the live data flow.** Verify the actual identity-provider/Auth0 setup, Streamlit hosting, Supabase project region, data fields stored in the learner_progress JSON bundle, logs, backups, retention, access controls, and any additional AI/chat provider. Do not infer hosting region, retention, or vendor processing from code alone.
- [ ] **Complete child-safety assessment and implementation before enabling child accounts.** Vocogni is an educational product likely to be used by children. Assess applicable age categories/risk levels and the exact requirements for minimum-age rules, age verification/assurance, parent/guardian consent, child-friendly design, reporting mechanisms, and risk controls under Indonesian child-protection rules. A self-declared checkbox by a child is not a substitute where verifiable parental/guardian consent is required. Do not use the Terms page itself as evidence that these steps are complete.
- [ ] **Record acceptance correctly.** Before treating the Terms as binding, implement an explicit acceptance step, store the version and timestamp of accepted Terms, and decide how material revisions will be presented. Where child consent is separately required, record it through the applicable verified process; do not conflate a child's click with a guardian's consent.
- [ ] **Provide account and data requests.** Establish a tested process for account closure, access/correction/deletion requests, child/guardian requests, complaints, and safety reports. Do not direct people to public issue trackers for private personal-data requests.
- [ ] **Test security and recovery.** Confirm access restrictions, least-privilege database credentials, log redaction, recovery/deletion behavior, and response procedures for unauthorized access or a personal-data incident.
- [ ] **Review educational claims.** Ensure course, question-review, coach, and progress wording does not claim educator validation, official grading, guaranteed learning outcomes, or psychometric validity where none has been established.
- [ ] **Verify third-party terms and contracts.** Review the actual terms, privacy documentation, data processing terms, transfer terms, and permissions for the identity, hosting, database, and any AI provider used in the deployed build.
- [ ] **Publish an effective date and change process.** Ensure the final Indonesian-language terms are readable, easy to access before account creation, and consistent with the Privacy Notice. Keep an archived copy of each published version.

## Implementation status in this code change

- [x] Added a bilingual draft in TERMS_OF_SERVICE.md.
- [x] Added a Terms page inside Vocogni and made the draft viewable from the sign-in screen.
- [x] Added a test that checks the Terms content and app wiring.
- [ ] No acceptance record or guardian-consent verification has been implemented by this change.
- [ ] No Privacy Notice has been created by this change.
- [ ] No live hosting/data-flow audit or legal counsel review has been performed.

## Official legal sources to review

1. **Law No. 27 of 2022 on Personal Data Protection (UU 27/2022)** — official Ministry of Communication and Digital Affairs JDIH: https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/  
   Article 25 addresses special handling and parent/guardian consent for processing children's personal data. Review the full law and its implementing framework.
2. **Government Regulation No. 17 of 2025 on Governance of Electronic System Operators for Child Protection (PP 17/2025)** — official BPK legal database: https://peraturan.bpk.go.id/Details/316698/pp-no-17-tahun-2025
3. **Minister of Communication and Digital Affairs Regulation No. 9 of 2026** implementing PP 17/2025 — official BPK legal database: https://peraturan.bpk.go.id/Details/346040/permenkomdigi-no-9-tahun-2026. This regulation covers matters including minimum age, age-band suitability, child-user verification, risk assessment, child-account profiles, and child-protection controls.
4. **Government Regulation No. 71 of 2019 on the Operation of Electronic Systems and Transactions (PP 71/2019)** — official JDIH: https://jdih.komdigi.go.id/produk_hukum/view/id/695/t/common
5. **Law No. 8 of 1999 on Consumer Protection (UU 8/1999)** — official BPK legal database: https://peraturan.bpk.go.id/Details/45288/uu-no-8-tahun-1999
6. **Law No. 24 of 2009 on the National Flag, Language, Emblem and Anthem (UU 24/2009)** — official BPK legal database: https://peraturan.bpk.go.id/Details/38661/uu-no-24-tahun-2009. Obtain advice on language requirements and publish an Indonesian version suitable for Indonesian users.

This list is a starting point, not an exhaustive determination of all applicable laws or the legal classification of Vocogni. The operator should ask Indonesian counsel to assess the current legal status, including electronic-system registration and any other obligations applicable to the actual deployed service.
