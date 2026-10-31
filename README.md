# Vocogni — Learning Prototype

Vocogni is an applied-learning prototype built around the loop:

**Diagnose → Understand → Practice → Apply / Transfer → Measure → Update**

The application uses Streamlit, Auth0 OIDC for authentication, and Supabase PostgreSQL for durable learner-state persistence. It remains a prototype and is not production-validated.

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
streamlit run app.py
```

Run from the project root (the folder containing `app.py`).

## Optional LLM tutoring

The Study Guide now combines two modes:

- **Local commands:** profile/progress/mistake summaries, recommendations, course listing, and navigation. These run without an external model.
- **Optional AI tutoring:** open-ended subject explanations and conversational learning support through an OpenAI-compatible Chat Completions provider.

AI tutoring is off by default and requires a session-only opt-in inside the Study Guide. It is not used by the answer checker, diagnostic scoring, progress persistence, or official mastery decisions.

### Configure a provider

The app accepts any provider that implements the OpenAI-compatible `POST /chat/completions` interface.

Set these environment variables on the server:

```bash
VOCogni_LLM_BASE_URL=https://YOUR_PROVIDER_BASE_URL/v1
VOCogni_LLM_MODEL=YOUR_MODEL_NAME
VOCogni_LLM_API_KEY=YOUR_SECRET_API_KEY
```

Or configure Streamlit secrets:

```toml
[llm]
base_url = "https://YOUR_PROVIDER_BASE_URL/v1"
model = "YOUR_MODEL_NAME"
api_key = "YOUR_SECRET_API_KEY"
```

For local development, place the TOML in `.streamlit/secrets.toml` (do not commit that file). For hosted Streamlit, add the values in the app's Secrets settings. Never put provider keys in Python source, Git, browser-side code, or learner-visible configuration.

If no complete provider configuration is present, the AI opt-in is disabled and local Study Guide commands continue to work. Provider-specific endpoint and model compatibility must be checked against the provider's documentation.

### What is sent to the provider

After the learner enables AI tutoring and submits an open-ended request, the server sends:
- the current message;
- up to eight recent Study Guide messages; and
- a limited learning summary that may include grade level, preferred learning settings, course-level accuracy, and recorded mistake tags.

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

The current pattern detector is a small, text-based heuristic. Full Learning Pattern Memory, structured attempt events, intervention tracking, and measured retention/transfer are not yet implemented.

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

## Tests

Run the offline tests:

```bash
python -m unittest discover -s tests -p 'test_ai_prototype.py' -v
python -m py_compile app.py vocogni_ai.py vocogni_assistant.py ai_prototype/llm.py ai_prototype/engine.py
```

These tests do not validate a live provider, deployed Auth0/Supabase integration, UI behavior, educational effectiveness, or legal compliance.
