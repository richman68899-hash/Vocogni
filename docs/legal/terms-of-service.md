# Terms of Use — Prototype Draft

**Status:** Draft for product and legal review. These terms are not ready to serve as the final public agreement. Complete the operator details, governing-law provisions, data-handling procedures, and legal review before public release.

- **Service operator:** [Insert the responsible individual or legal entity]
- **Support contact:** [Insert a monitored support contact]
- **Effective date:** [Set after review]
- **Version:** 0.1-draft

## 1. What Vocogni is

Vocogni is an educational learning prototype. Depending on the current release, it may provide authored lessons, practice questions, rule-based diagnostics, answer feedback, course progress, learning notes, milestones, and recommendations based on recorded activity. Features can change as the prototype develops.

The current Vocogni Assistant is a **rule-based helper**, not a general-purpose generative AI chatbot. It matches supported requests to existing code and the learner data passed to it. In the current implementation it does not call an external generative AI model.

## 2. Who may use the service

Learners should use Vocogni in an age-appropriate way. If you are under the age at which you can independently consent to online services or personal-data processing under applicable law, a parent or legal guardian should review the service and provide any permission required by law. A school or educator using Vocogni with learners should obtain the permissions and provide the notices required for its setting.

The operator must confirm the age rules, guardian-consent flow, and school-use requirements before opening the service to the public. The current prototype does not verify or record parent/guardian consent, and a documented child-safety risk assessment has not been completed. For that reason, this build must not be treated as cleared for public child-facing use. Displaying this draft does not record or prove consent.

For an Indonesian launch, the operator's review should assess the Personal Data Protection Law (Law No. 27 of 2022), Government Regulation No. 17 of 2025 on child protection in electronic systems, and Minister of Communication and Digital Regulation No. 9 of 2026, alongside other rules that qualified counsel determines apply. This is a launch-review requirement, not a legal conclusion about the operator's obligations.

## 3. Accounts and learner information

Authentication is handled through Auth0. The application stores learner-state information in Supabase so that supported information can persist between sessions. Depending on what you enter or use, this can include profile fields, learning preferences, course progress, practice attempts, notes, and milestones.

Keep your sign-in credentials private. Do not share an account or attempt to view, change, or access another learner's data.

The separate Privacy Notice describes the current data categories and important items that still require confirmation before public launch.

## 4. Acceptable use

Use Vocogni lawfully and respectfully. Do not:

- attempt to access another user's account or records, bypass access controls, interfere with the service, or test security without written authorization;
- upload or save personal information about another person without an appropriate right and permission;
- use the service to harass, threaten, exploit, impersonate, or expose another person;
- introduce malicious code, disrupt operation, or misuse the service;
- present Vocogni's practice results, recommendations, or diagnostics as official grades, professional assessments, or certified qualifications; or
- use learning tools to misrepresent work as your own where your school or educator prohibits that conduct.

The operator should establish a clear process for reporting misuse and handling complaints before public launch.

## 5. Educational limitations

Vocogni is a learning aid, not a school, teacher, examination board, or accredited assessment provider. Lessons and feedback may be incomplete, simplified, or incorrect. Rule-based diagnostics and progress summaries are prototypes; they are not validated psychometric tests, definitive judgments of ability, or guarantees of future academic performance.

Check important answers against course materials, a teacher, or another reliable educational source. You remain responsible for deciding how to use learning guidance and for reviewing work before submitting it.

Vocogni is not designed to provide medical, mental-health, legal, financial, or emergency advice.

## 6. Your content

You remain responsible for content you choose to enter, including notes and profile details. Do not enter material you are not entitled to use or disclose. The operator must define final rules for content ownership, permitted licenses, intellectual-property complaints, and removal requests before public launch.

## 7. Third-party services

The current architecture uses third-party services for authentication, hosting, and storage, including Auth0 and Supabase. These services may process technical or account information as needed to operate their respective parts of the product. The operator must publish the actual provider list, applicable terms, hosting/data regions, and cross-border processing details before launch.

## 8. Availability, changes, and account closure

This is a developing prototype. Features may be unavailable, revised, or removed, and saved records may not be available during outages or maintenance. Do not treat the prototype as the only place to keep important schoolwork; keep your own copy of anything you cannot afford to lose.

The final service must explain how a user or guardian can request account closure, access to records, correction, and deletion. A complete self-service account-deletion flow is not currently documented as available, so this draft does not promise that functionality.

## 9. Disclaimers and responsibility

The service is provided as a prototype for educational support. To the extent permitted by applicable law, the operator cannot guarantee that all content, scoring, recommendations, saving, or availability will be uninterrupted or error-free. Nothing in the final terms should exclude or limit rights or obligations that cannot legally be excluded or limited.

## 10. Complaints and contact

Use **[insert monitored support and privacy contact]** to report a problem, request help, or raise a privacy concern. Replace this placeholder with a real, monitored contact before public release.

## 11. Governing law and dispute process

**To be completed after legal review.** The operator must identify the responsible legal entity, applicable governing law, complaint channels, and dispute process in the final public terms.

## 12. Changes to these terms

The final version should display its effective date and version and explain how material changes will be communicated. Do not rely on this draft as a substitute for completing a clear, reviewable acceptance process where one is required.
