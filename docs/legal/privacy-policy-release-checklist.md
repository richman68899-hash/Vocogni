# Privacy Policy — Publication and Compliance Checklist

**Status:** Required before public launch  
**Related document:** [`PRIVACY_POLICY.md`](../../PRIVACY_POLICY.md)  
**Review date:** 28 October 2026

This checklist is an internal release gate. Creating a privacy policy is necessary but does not itself make the product's processing lawful or establish that technical safeguards are in place.

## 1. Identify the controller and contact

- [ ] Choose the actual person or legal entity responsible for Vocogni's processing decisions.
- [ ] Record its full legal name and address.
- [ ] Create and test a monitored privacy contact address.
- [ ] Have an adult responsible operator and qualified Indonesian legal adviser review ownership, capacity, and launch responsibilities before processing real learners' data.
- [ ] Replace every placeholder in `PRIVACY_POLICY.md`; do not publish placeholder text.

## 2. Children's data — release blocker

The PDP Law (Law No. 27 of 2022), Article 25, requires special treatment of children's personal data and parent/guardian consent. Current legal reporting says Government Regulation No. 33 of 2026 takes effect on **16 January 2027** and adds more detailed operational obligations, including identifying child users and verifying parental/guardian consent. Confirm the enacted text and any later official guidance with Indonesian counsel before release.

- [ ] Decide and document the permitted user-age range.
- [ ] Implement age identification or age assurance appropriate to the service and legal review.
- [ ] Implement a parent/guardian consent process before processing children's personal data.
- [ ] Verify the consent is valid; record what was consented to, by whom, when, and which notice/version applied.
- [ ] Separate data-processing consent from acceptance of general Terms of Service.
- [ ] Implement consent withdrawal, child/guardian access and deletion requests, and a process for the transition when a user reaches adulthood.
- [ ] Test that children cannot bypass the consent gate by directly opening a route, logging in through the identity provider, or reusing an existing session.

**Current code gap:** this repository's existing authentication and learner-state persistence flow does not establish a verified age-identification or parent/guardian consent workflow. Do not treat a written policy or a checkbox acknowledging the Terms of Service as a substitute for that workflow.

## 3. Data inventory and lawful basis

- [ ] Inventory every field and data flow: identity claims; profile; lessons, diagnostic responses and practice attempts; notes and folders; milestones; settings; assistant messages in session state; technical/security logs; and any assets/uploads enabled in the deployed build.
- [ ] For every purpose, identify and document the applicable lawful basis. Do not assume consent to general Terms of Service covers every processing purpose.
- [ ] Confirm that profile fields are optional where feasible and that data collected is limited to what the feature needs.
- [ ] Review the diagnostic and recommendation outputs for risks related to profiling or systematic evaluation of learners.
- [ ] Create and maintain a record of processing activities and a data-flow diagram.
- [ ] Assess whether a data-protection impact assessment is required for the intended scale, child data, learner scoring/profiling, and technology.

## 4. Providers and cross-border data

- [ ] Confirm the exact Auth0 tenant and identity provider configured for production.
- [ ] Confirm Supabase project region, data residency options, backup locations, and deletion behaviour.
- [ ] Confirm Streamlit hosting region and applicable logging/support access.
- [ ] Confirm whether the browser still loads Google Fonts from Google's servers; either disclose it accurately or self-host the fonts after checking licensing and implementation.
- [ ] Review provider privacy notices, data-processing agreements, subprocessors, security terms, and retention/deletion controls.
- [ ] Record which providers receive which data and why.
- [ ] Assess international-transfer requirements and document the legal basis and safeguards. Do not say data stays in Indonesia unless the actual architecture supports that claim.
- [ ] Re-check the provider list whenever the product adds analytics, email services, file storage, payments, or a generative-AI model.

## 5. Retention, user rights, and deletion

- [ ] Define documented retention durations by category and the event that starts the retention period.
- [ ] Implement account/data deletion and verify that the relevant Supabase learner record and associated content are deleted.
- [ ] Confirm what remains in provider backups and logs, and document when those copies expire.
- [ ] Implement a privacy-request workflow for access, correction, deletion, withdrawal, and other applicable rights.
- [ ] Verify the requester and route child requests to the parent/guardian workflow where required.
- [ ] Test request tracking, deadlines, completion evidence, and notice to the requester.
- [ ] Ensure no feature advertises self-service deletion until the feature exists and has been tested.

## 6. Security and incidents

- [ ] Review database permissions and confirm one signed-in learner cannot read or overwrite another learner's record.
- [ ] Verify server-only secrets are not committed, logged, or included in front-end assets.
- [ ] Test authentication, session expiry, logout, failed-save recovery, backups, and account isolation.
- [ ] Document staff/operator access and restrict it to people who need it.
- [ ] Create a personal-data incident response procedure and a method for identifying affected records.
- [ ] Confirm the applicable breach-notification requirements and timing, including the PDP Law's 3 x 24-hour notice requirement where it applies.
- [ ] Run the relevant application security checks before enabling real student accounts.

## 7. Public presentation and consent records

- [ ] Add a visible Privacy Policy link before sign-in and within the authenticated product.
- [ ] Add a visible Terms of Service link once that separate document has been drafted and reviewed. No Terms of Service file was found in the `main` branch tree on 28 October 2026.
- [ ] Use a clear, accessible version date and retain previous versions.
- [ ] Provide separate, unambiguous consent controls wherever consent is the lawful basis, including parent/guardian consent for children's data where required.
- [ ] Store evidence of the consent action and the exact notice version.
- [ ] Do not launch while the policy contains placeholders or while the child-consent, retention, deletion, and data-transfer gaps remain unresolved.

## Current legal sources to review

1. Indonesia, Law No. 27 of 2022 on Personal Data Protection — official Ministry of Communication and Digital Affairs legal database: https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/
2. Indonesia, Law No. 27 of 2022 — official BPK regulations database: https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022
3. Current practitioner update on Government Regulation No. 33 of 2026 and its expected 16 January 2027 effective date: https://www.pwc.com/id/en/pwc-publications/services-publications/digital-publications/government-regulation-33-2026-personal-data-protection.html

Legal status and implementation guidance should be re-verified at the time of launch. This checklist is operational guidance, not legal advice.
