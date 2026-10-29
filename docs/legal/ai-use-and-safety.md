# AI Use and Safety Notes — Prototype

**Status:** Prototype draft — user-facing guidance for the current build. Review it whenever learning, assistant, scoring, storage, or model integrations change.

## 1. What the current assistant actually does

The floating Vocogni Study Guide currently supports a limited set of predictable requests, such as summarising profile fields, showing recorded mistakes, summarising saved progress, suggesting the next step from rule-based logic, listing courses, summarising notes/milestones/settings, and navigating to supported pages.

It uses predefined code paths and recorded Vocogni data. It **does not currently use a connected generative AI model** and cannot answer every open-ended subject question. Unrecognised questions may receive a supported-request message rather than a substantive explanation.

Course lessons, feedback, and diagnostics may use authored content or deterministic rules. A label such as “assistant,” “personalised,” or “diagnostic” does not mean that a generative model is involved or that a result has been independently validated.

## 2. Use it as a learning aid, not an authority

- Check important explanations and answers against your course materials, textbook, or teacher.
- Treat diagnostics, practice percentages, and recommendations as limited evidence from the recorded items—not as official school grades, a full measure of intelligence, a diagnosis, or a guarantee of future performance.
- Ask a teacher for help when a result seems wrong or a concept remains unclear.
- Review and understand your work before submitting it. Follow your school's academic-integrity rules.
- Do not use Vocogni as a substitute for qualified medical, mental-health, legal, financial, or emergency support.

## 3. Protect your privacy

Do not put passwords, authentication codes, financial information, private contact details, precise location, or sensitive medical/mental-health information into notes or other fields unless the service specifically requires it and its handling has been clearly explained. Do not enter confidential information about classmates, teachers, or other people without permission.

The assistant may display information already stored in your Vocogni profile, progress, notes, settings, or milestones. Anyone who can access your signed-in session may be able to see what is displayed, so sign out on shared devices and keep your credentials private.

The current assistant does not send its inputs to an external generative AI model, but the application still uses its hosting, authentication, and database services to operate. See the Privacy Notice for the current architecture and the deployment details that remain to be confirmed.

## 4. Safer use by younger learners

> **Quick read for younger learners**
> - If you are under 18, ask a parent/guardian or teacher to review Vocogni with you.
> - If something here makes you feel unsafe or exposes private information, tell a trusted adult.
> - Vocogni is not watched live. Do not rely on it to get urgent help.
> - This prototype is not cleared for public child-facing use until the required checks and safeguards are complete.

If you are under 18, involve a parent/guardian or educator as appropriate. Tell a trusted adult if something on the service makes you feel unsafe, exposes private information, or appears to be used to target or harm another learner.

**Product-readiness warning:** This prototype does not verify or record parent/guardian consent and has no documented child-safety risk classification. These notes do not replace legally required consent, age-appropriate controls, or risk mitigation. Public child-facing use should remain blocked until the operator completes a jurisdiction-specific legal review and implements the required controls. For Indonesia, see the official child-data and electronic-system child-protection references in the Privacy Notice.

Do not use the service to bully, threaten, exploit, impersonate, or expose others. Report concerns through **NOT CONFIGURED — a verified monitored safety/support contact has not been published. This remains a launch blocker.** once the operator has filled in and verified that contact.

## 5. Limits of safeguards

The current Study Guide is a narrow rules-based feature, not a human moderator and not an emergency-monitoring service. These notes describe responsible use; they do not guarantee that every harmful request or unsafe situation will be detected. Do not assume the app is monitored in real time.

## 6. Before any future generative AI integration

Do not connect a live model and silently reuse the current notice. Before release, the operator should:

1. identify the model/service provider and the exact categories of data sent to it;
2. document purpose, data location/transfer, retention, provider use of inputs, training controls, and available opt-out/consent choices;
3. minimise or redact personal data from prompts, and never send private learner notes or profile details unless necessary, justified, and properly disclosed;
4. test for fabricated answers, inappropriate content, privacy leakage, prompt injection, discrimination, and unsafe educational advice;
5. distinguish model-generated content from authored or verified material in the interface;
6. establish a way to report incorrect or unsafe output, review incidents, and disable the feature; and
7. update the Terms of Use and Privacy Notice and obtain any required permissions before enabling the change.

## 7. Reporting issues

Contact **NOT CONFIGURED — a verified monitored safety/support contact has not been published. This remains a launch blocker.** to report an incorrect result, a privacy concern, harmful content, or a technical issue. This placeholder must be replaced with a monitored channel before public release.
