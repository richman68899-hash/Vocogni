# AI Learning Core — Integrated Prototype

**Branch:** `feature/ai-learning-core-prototype`  
**Status:** integrated into the Study Guide on this feature branch; not merged into `main`.

## Scope

This feature combines:

1. **Natural-language tutoring:** optional OpenAI-compatible Chat Completions for open-ended questions and explanations.
2. **Local learner-data commands:** deterministic summaries and navigation remain available without a model provider.
3. **Learning-pattern recognition:** transparent heuristics identify explicit text signals. They are not trained machine learning, do not infer a learner's mental state, and do not establish a misconception.

## Application integration

- `app.py`: renders the integrated Study Guide from `vocogni_ai.py`.
- `vocogni_ai.py`: session-only opt-in, provider configuration, minimal learner context, and chat UI.
- `vocogni_assistant.py`: deterministic profile/progress/mistake/course commands and navigation.
- `ai_prototype/llm.py`: standard-library HTTP adapter for OpenAI-compatible chat completions.
- `ai_prototype/engine.py`: system prompt, bounded conversation history, context, pattern signals, and fallback.
- `ai_prototype/patterns.py`: heuristic text patterns and aggregation.
- `ai_lab_app.py`: remains a standalone sandbox for isolated experiments.
- `tests/test_ai_prototype.py`: offline unit tests for patterns, provider config, context boundaries, and engine orchestration.

## Runtime behavior

- The assistant remains available in the Learn/Browse flow.
- Local account-data shortcuts do not call the external provider.
- Open-ended requests call the provider only when all credentials are configured and the learner has enabled the session-only opt-in.
- If no provider is configured, the opt-in control is disabled and local commands still work.
- Provider errors produce a local fallback instead of crashing the app.
- AI-generated messages are labelled in the UI.

## Configuration

Use server environment variables:

- `VOCogni_LLM_BASE_URL`
- `VOCogni_LLM_MODEL`
- `VOCogni_LLM_API_KEY`

Or Streamlit secrets:

```toml
[llm]
base_url = "https://YOUR_PROVIDER_BASE_URL/v1"
model = "YOUR_MODEL_NAME"
api_key = "YOUR_SECRET_API_KEY"
```

No provider or API key is bundled with the repository. The adapter requires the OpenAI-compatible `POST /chat/completions` API.

## Data minimisation

When AI is enabled, the request includes the current message, up to eight recent chat messages, and a limited learner summary. The summary may include grade level, selected learning preferences, course-level accuracy, and recent mistake tags.

The application does not add the learner's name, email, account ID, saved notes, milestones, age, or country to that summary. A learner can still type personal information into chat, so the interface warns against sharing sensitive details.

Provider retention, training, subprocessors, and data location depend on the configured provider. The session opt-in does not verify or record parent/guardian consent and does not establish legal compliance.

## System boundaries

The LLM generates explanations and conversational text. It does not:
- mark answers correct or incorrect;
- alter verified answer keys or scoring;
- write learner progress to Supabase;
- independently declare mastery;
- confirm a recurring misconception; or
- automatically classify every learner mistake.

The Progress summary and lesson diagnostics remain deterministic. Full Learning Pattern Memory, structured attempt events, intervention tracking, and measured retention/transfer are not yet implemented.

## Known limitations

- Only OpenAI-compatible chat-completions providers are supported.
- No streaming, tool calling, multimodal input, embeddings, retrieval, fine-tuning, or model fallback chain.
- Model output can be incorrect, inconsistent, or inappropriate; the prompt is not a substitute for safety testing or human review.
- Existing learning context is based on current progress aggregates and mistake tags, not a persistent LPM evidence ledger.
- No live provider call, Streamlit deployment, educational-quality evaluation, or legal compliance review has been verified in this change.
- Public child-facing use remains blocked pending provider review, required consent mechanisms, privacy/security work, and child-safety assessment.

## Tests

```bash
python -m unittest discover -s tests -p 'test_ai_prototype.py' -v
python -m py_compile app.py vocogni_ai.py vocogni_assistant.py ai_prototype/llm.py ai_prototype/engine.py
```
