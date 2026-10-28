# Vocogni AI Use and Safety Notes — Working Draft

**Status:** Internal product draft — not approved for public release  
**Prepared:** 28 October 2026

> **Current implementation notice:** In the repository version reviewed for this policy, the floating Vocogni Assistant is a rule-based helper, not a generative-AI chatbot. It uses keyword/request matching to show limited summaries from information already in the app. It does not call an external LLM. Course diagnostics and several recommendations are also deterministic rules. This must be updated if the implementation changes.

## 1. What the assistant can and cannot do today

The assistant currently supports a limited set of operations, including:
- summarising profile fields the learner has entered;
- summarising recorded progress and practice accuracy;
- listing saved practice mistakes when available, or aggregate mistake themes;
- suggesting a next step using the existing rule-based coach;
- listing courses, summarising note titles/milestones, and showing settings; and
- navigating to supported app sections.

It does not understand every open-ended question, independently research the web, teach every subject through a language model, or reliably infer a learner's knowledge, personality, health, or ability. For unsupported requests, it should say that the request is not supported rather than inventing an answer.

## 2. Treat outputs as help, not authority

- Check explanations and results against a teacher, textbook, worked solution, or reliable source.
- Practice accuracy, diagnostic placement, and recommendations are limited evidence. They are not official grades, clinical assessments, or validated measurements of intelligence, mastery, or learning gain.
- A single wrong answer does not prove a stable weakness. A rule-based suggestion is a review prompt, not a label about the learner.
- Do not use Vocogni alone to make consequential decisions about education, health, legal matters, finances, or safety.
- Ask a teacher, parent/guardian, or other qualified person to review important work and decisions.

## 3. Protect your privacy

Do not enter:
- passwords, authentication codes, or API keys;
- government ID/passport numbers or payment-card details;
- precise home addresses, live location, or private contact details;
- detailed medical, mental-health, or other highly sensitive information;
- confidential reports, private school records, or another person's personal information without permission.

Use the minimum information needed for a learning task. Check notes and profile fields before sharing your screen or using a shared device. Log out on devices other people can access.

The current assistant reads session data such as profile fields, saved progress, settings, notes, and milestones when answering supported requests. Its conversation messages are held in the app session; they are not written by this helper to an external generative-AI provider. The hosting and database providers may still process the data needed to run the app. See the **Privacy Notice** in the in-app Trust & Safety page.

## 4. Appropriate use and academic integrity

Use Vocogni to understand concepts, practise, reflect on mistakes, and plan study. Do not use it to bully or threaten others, expose private information, impersonate another learner, bypass account controls, or present generated or copied work as your own where your teacher's rules prohibit that.

If a feature helps you produce an answer, make sure you understand the steps and follow your school's academic-integrity rules.

## 5. Child and learner safety

The prototype may be used by school-age learners. It does not currently verify or record parent/guardian consent, provide a complete child-safety reporting channel, or implement a full child-safety risk assessment. Adult oversight in this notice is not a substitute for legally required consent and product controls.

The owner must finish a jurisdiction-specific review and implement required child/guardian consent, age-appropriate design, risk assessment, complaint/reporting, and incident-handling processes before public child access. Relevant Indonesian references include [Law No. 27 of 2022 on Personal Data Protection](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/), [Government Regulation No. 17 of 2025](https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025), and [Minister Regulation No. 9 of 2026](https://jdih.komdigi.go.id/produk_hukum/view/id/1007/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Bdigital%2Bnomor%2B9%2Btahun%2B2026). These references do not by themselves establish compliance.

For a distressing or urgent safety situation, do not rely on the app. Stop and contact a trusted adult or appropriate local emergency/support service. Do not disclose sensitive details in the assistant.

## 6. Handling unsafe, misleading, or incorrect responses

If the assistant displays an inaccurate, inappropriate, or confusing answer:
1. Do not act on it as an authority.
2. Check the information with a teacher or trusted adult if it affects you or another person.
3. Report the issue through the product's published support channel when one exists.

**The current prototype does not yet have a monitored support/reporting contact.** A real contact and response process must be configured before public release. Until then, stop using the relevant feature and tell a parent/guardian or educator about serious concerns.

## 7. Rules for future AI integrations

No external AI provider should be enabled merely by adding an API call. Before release, each provider integration must have:
- a documented data-flow inventory stating exactly which learner, profile, progress, note, source, and prompt fields are sent;
- a provider review covering retention, model-training use, processing region, subprocessors, security, age restrictions and applicable contractual terms;
- data minimisation, access control, safe error/fallback behavior, rate limits, and tests that prevent data from one learner reaching another;
- clear in-product disclosure before data is sent, plus any required consent or guardian approval;
- clear distinctions between authored/verified content, model-generated drafts, and reviewed material;
- prompt-injection and untrusted-source handling where learner documents are used;
- content safeguards, human escalation for consequential concerns, incident reporting, and a way to disable the feature; and
- updated terms, privacy notice, AI notes, and test coverage before deployment.

Model-generated questions must not automatically be called verified. They should pass Vocogni's existing question-validation and review process before being represented as verified instructional content.

## 8. Development safeguards checklist

Before any public launch, the owner must confirm:
- [ ] Legal operator name and monitored support/privacy contact are published.
- [ ] Child-safety/product-risk assessment is complete and documented.
- [ ] Applicable guardian-consent and age-appropriate access flow is implemented and tested.
- [ ] Privacy rights requests, retention, export, correction, deletion, and backup deletion are implemented or clearly defined.
- [ ] Auth0/Streamlit/Supabase configuration, processing region, access controls, and retention settings are checked.
- [ ] Account-isolation and save/reload behavior are tested with multiple accounts.
- [ ] Every AI/provider data flow has been documented; this policy matches shipped code.
- [ ] Terms, privacy notice, and AI safety notes are reviewed by qualified counsel and translated appropriately for the intended users.
- [ ] A monitored incident/safety report process and response owner are in place.

This checklist is a minimum development gate, not a certification of legal compliance.
