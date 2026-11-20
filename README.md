# Vocogni — Learning Prototype

Vocogni is an applied-learning prototype built around the loop:

**Diagnose → Understand → Practice → Apply / Transfer → Measure → Update**

The application uses Streamlit, Auth0 OIDC for authentication, and Supabase PostgreSQL for durable learner-state persistence. It remains a prototype and is not production-validated.

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
# Private operator preview only; keep the deployment access-restricted.
# Do not set this on a public learner-facing deployment.
export VOCogni_INTERNAL_PREVIEW=true
streamlit run app.py
```

Run from the project root (the folder containing `app.py`). On Windows PowerShell, set the private-preview flag with `$env:VOCogni_INTERNAL_PREVIEW = "true"` before starting Streamlit.

### Child-facing release gate

Normal learner access is **blocked by default**. The source does not yet implement a verified guardian-consent workflow or a monitored safeguarding contact, and the legal/operator review is not complete. The app therefore stops before authentication and before loading learner data unless the operator explicitly enables a private preview with `VOCogni_INTERNAL_PREVIEW=true`.

That flag is strictly for a restricted operator preview using synthetic accounts and data. It is **not** a public-launch switch, does not verify consent, does not establish legal compliance, and must not be set on a public deployment. Public child-facing access must remain disabled until the outstanding launch-readiness requirements have been completed and the release process has been reviewed by the responsible operator and qualified counsel.

## Optional LLM tutoring

The Study Guide now combines two modes:

- **Local commands:** profile/progress/mistake summaries, recommendations, course listing, and navigation. These run without an external model.
- **Optional AI tutoring:** open-ended subject explanations and conversational learning support through an OpenAI-compatible Chat Completions provider.

AI tutoring is off by default and requires (1) an explicit server-side feature toggle, (2) a separate operator acknowledgement that provider review is complete, and (3) a session-only learner opt-in inside the Study Guide. Missing or unreadable review configuration fails closed. It is not used by the answer checker, diagnostic scoring, progress persistence, or official mastery decisions.

### Configure a provider

The app accepts any provider that implements the OpenAI-compatible `POST /chat/completions` interface.

Set these environment variables on the server:

```bash
VOCogni_LLM_BASE_URL=https://YOUR_PROVIDER_BASE_URL/v1
VOCogni_LLM_MODEL=YOUR_MODEL_NAME
VOCogni_LLM_API_KEY=YOUR_SECRET_API_KEY
# Only after documenting provider retention, training, region, subprocessors,
# security, and child-safeguarding review:
VOCogni_ENABLE_EXTERNAL_AI_TUTORING=false
VOCogni_LLM_PROVIDER_REVIEWED=false
```

Or configure Streamlit secrets:

```toml
[llm]
base_url = "https://YOUR_PROVIDER_BASE_URL/v1"
model = "YOUR_MODEL_NAME"
api_key = "YOUR_SECRET_API_KEY"
enable_external_ai_tutoring = false
provider_review_completed = false
```

For local development, place the TOML in `.streamlit/secrets.toml` (do not commit that file). For hosted Streamlit, add the values in the app's Secrets settings. Never put provider keys in Python source, Git, browser-side code, or learner-visible configuration.

If no complete provider configuration is present, the feature toggle is off, or the separate provider-review acknowledgement is absent, the AI opt-in is disabled and local Study Guide commands continue to work. Set `VOCogni_ENABLE_EXTERNAL_AI_TUTORING=true` and `VOCogni_LLM_PROVIDER_REVIEWED=true` (or the matching `[llm]` secrets) only after recording the provider's retention, training use, subprocessors, security, data location, cross-border processing, and child-safeguarding review. This acknowledgement is an operator control, not proof of legal compliance or guardian consent. Provider-specific endpoint and model compatibility must be checked against the provider's documentation.

### What is sent to the provider

After the learner enables AI tutoring and submits an open-ended request, the server sends:
- the current message;
- up to eight messages from previous AI-tutoring turns, only when the separate saved chat-history choice is enabled; and
- a limited learning summary that may include grade level, preferred learning settings, course-level accuracy, and recorded mistake tags, only when the separate saved-learning-summary choice is enabled.

Both optional sharing preferences are off by default. The current message is still sent when the learner explicitly uses external AI tutoring. These preferences do not replace any legally required parent/guardian permission.

The code does not add the learner's name, email, account ID, saved notes, milestones, age, or country to that summary. A learner can still type private information into the chat, so the interface warns against doing so. Provider retention, training, subprocessors, and data location depend on the configured provider and its terms.

The session opt-in is not persisted. Local account-data commands do not need an external AI call.

## Architecture

- `app.py` — authentication, navigation, persistence coordination, and app routing.
- `vocogni_ai.py` — integrated Study Guide UI, session opt-in, provider configuration, and minimal learner context.
- `vocogni_assistant.py` — deterministic account-data commands and navigation.
- `ai_prototype/llm.py` — standard-library HTTP adapter for OpenAI-compatible providers.
- `ai_prototype/engine.py` — prompt orchestration, bounded history/context, and fallback.
- `ai_prototype/patterns.py` — explainable heuristic pattern recognition; not a trained model or validated diagnosis.
- `logic.py` — answer checking, progress aggregation, and rule-based learning logic.
- `state.py` — learner session state and durable persistence coordination.
- `sections/*.py` — learner-facing app sections.

## Important system boundaries

The LLM generates explanations and conversational text. It does not:
- mark answers correct or incorrect;
- alter verified answer keys or grading;
- create durable learner progress;
- independently declare mastery;
- confirm a recurring misconception; or
- automatically label every learner error.

The current pattern detector is a small, text-based heuristic, not a trained model. The learning-memory module stores aggregate skill and rubric evidence. Course lessons also record explicit exposures to concept explanations, worked examples, hints, answer feedback, and targeted repair cues. The Progress page links each recorded support to up to the next three verified answers for that skill. This is descriptive sequencing, not causal evidence that a support worked. Scheduled delayed-retention checks and validated learning-effectiveness measurements are not yet implemented.

## Privacy, safety, and deployment limits

- This prototype does not verify or record parent/guardian consent.
- The session opt-in does not replace legally required consent or a child-safety review.
- Provider privacy/retention/training terms must be reviewed before real learner data is sent.
- Do not use real learner data until data minimisation, provider review, access controls, retention/deletion, and applicable legal requirements have been addressed.
- The model may hallucinate or provide incorrect explanations. Check important answers with trusted course materials or a teacher.
- The app is not monitored live and does not provide emergency support.
- Legal notices remain drafts; public child-facing deployment should remain blocked pending appropriate review and safeguards.

See:
- `docs/legal/ai-use-and-safety.md`
- `docs/legal/privacy-notice.md`
- `docs/features/ai-learning-core-prototype.md`
- `docs/features/ai-learning-core-integration.md`

## Tests and beta verification

Install the project requirements, then run the **full** automated suite from the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q -x '(^|[\\/])(\\.git|\\.venv|venv)([\\/]|$)' .
```

The AI prototype tests can also be run separately while working on that feature:

```bash
python -m unittest discover -s tests -p 'test_ai_prototype.py' -v
```

GitHub Actions runs the full test suite and a Python compilation check. Passing automated checks does **not** validate live Auth0 login/session behavior, Supabase account isolation, deployed persistence recovery, actual-device usability, question correctness, educational effectiveness, or legal compliance.

Before a learner pilot, complete the evidence-based [Stage 1 beta acceptance checklist](docs/testing/stage1-beta-acceptance.md), the [lesson diagnostics acceptance tests](docs/testing/lesson-diagnostics-acceptance.md), and the [legal and safety launch-readiness checklist](docs/legal/launch-readiness.md). Use synthetic accounts and data until the applicable privacy, consent, and learner-safeguarding gates are complete.
