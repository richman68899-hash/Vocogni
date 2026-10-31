# AI Use and Safety Notes — Prototype

**Status:** Prototype draft — review this notice whenever the assistant, provider, data flow, or safety controls change. This is not a final legal notice or proof of compliance.

## 1. What the Study Guide does

Vocogni has two distinct assistant modes:

- **Local Study Guide commands:** use application code and saved Vocogni data to summarise profile fields, show recorded mistakes, summarise progress, suggest a rule-based next step, list courses, summarise notes/settings, and navigate to supported pages. These commands do not require an external generative AI call.
- **Optional AI tutoring:** can answer open-ended subject questions and explain concepts using a configured OpenAI-compatible Chat Completions provider. It is disabled by default and requires the learner to turn on the session-only opt-in control in the Study Guide.

The optional model is a language-generation aid. It is not the source of truth for answer keys, official grades, mastery, or learner history. It may produce incorrect, incomplete, or misleading responses.

## 2. What is sent when AI tutoring is enabled

When the learner enables AI tutoring and sends an open-ended request, Vocogni sends to the configured provider:

- the current message;
- up to eight recent messages in the Study Guide conversation; and
- a limited learning-context summary, which may include grade level, preferred language/difficulty/feedback style, course-level practice accuracy, and recorded mistake tags.

The application code does not add the learner's name, email, account ID, saved notes, milestones, age, or country to that summary. This is data minimisation, not a guarantee that a learner cannot type personal information into the message or chat history. Learners must not enter private or sensitive information.

The provider receives the request over HTTPS using a server-side API key. The key must be stored in Streamlit secrets or environment variables, never in source code or browser-side code.

## 3. Choice and provider configuration

- AI tutoring is off by default.
- The opt-in applies only to the current Streamlit session and is not saved as a learner preference.
- If no provider is configured, the opt-in control is unavailable and local commands continue to work.
- The provider is configured by the operator using `VOCogni_LLM_BASE_URL`, `VOCogni_LLM_MODEL`, and `VOCogni_LLM_API_KEY`, or an `[llm]` section in Streamlit secrets.
- The operator must identify the actual provider and review its terms, retention, training use, subprocessors, security, data location, and cross-border transfer arrangements before enabling real learners.

The opt-in control is a product-level choice; it does not by itself establish that all legally required permissions or child-specific consent have been obtained.

## 4. Use it as a learning aid, not an authority

- Check important explanations and answers against your course materials, textbook, or teacher.
- Treat diagnostics, practice percentages, and recommendations as limited evidence from recorded items—not as official school grades, a full measure of intelligence, a diagnosis, or a guarantee of future performance.
- Ask a teacher for help when a result seems wrong or a concept remains unclear.
- Review and understand your work before submitting it. Follow your school's academic-integrity rules.
- Do not use Vocogni as a substitute for qualified medical, mental-health, legal, financial, or emergency support.

## 5. Protect your privacy

Do not put passwords, authentication codes, financial information, private contact details, precise location, or sensitive medical/mental-health information into the assistant, notes, or other fields. Do not enter confidential information about classmates, teachers, or other people without permission.

When AI tutoring is enabled, the current message and bounded conversation context are transmitted to the configured provider. Provider handling depends on the provider's contract and settings; Vocogni does not make a blanket promise that provider inputs are never retained or used for training. See the Privacy Notice.

## 6. Safer use by younger learners

> **Quick read for younger learners**
> - AI tutoring is optional and off by default.
> - Ask a parent/guardian or teacher to review the provider and its privacy terms before using external AI.
> - If something here makes you feel unsafe or exposes private information, tell a trusted adult.
> - Vocogni is not watched live. Do not rely on it to get urgent help.
> - This prototype is not cleared for public child-facing use until the required checks and safeguards are complete.

The current prototype does not verify or record parent/guardian consent and has no documented child-safety risk classification. These notes do not replace legally required consent, age-appropriate controls, or risk mitigation. Public child-facing use should remain blocked until the operator completes a jurisdiction-specific legal review and implements the required controls.

Do not use the service to bully, threaten, exploit, impersonate, or expose others. **Reporting channel: not configured.** A verified, monitored safety contact must be published before public launch; do not treat this draft as a working reporting channel.

## 7. Limits of safeguards

The local Study Guide is a narrow rules-based feature. Optional AI tutoring is a model-generated feature, not a human moderator or an emergency-monitoring service. The model can hallucinate, misunderstand working, reproduce biased assumptions, or respond poorly to adversarial prompts. The current integration does not provide live human moderation, guaranteed harmful-content detection, validated learning diagnosis, or verified answer checking.

## 8. Before public or school deployment

The operator must:
1. identify the actual model provider and categories of data sent;
2. document provider retention, training use, data location, subprocessors, and transfer arrangements;
3. complete the applicable privacy, child-safety, and consent review;
4. test fabricated answers, inappropriate content, prompt injection, privacy leakage, and unsafe educational advice;
5. add monitoring, incident review, user reporting, and a provider kill switch;
6. evaluate answer quality and age-appropriate behavior across representative subjects and question types; and
7. update the Terms of Use and Privacy Notice and obtain required permissions before enabling the feature for real learners.

## 9. Reporting issues

**Reporting channel: not configured.** A verified, monitored safety contact must be published before public launch so users can report an incorrect result, a privacy concern, harmful content, or a technical issue.
