# Integrated LLM Study Guide — Prototype

**Branch:** `feature/ai-learning-core-prototype`  
**Entry point:** `app.py`  
**UI:** `vocogni_ai.py`  
**Provider adapter:** `ai_prototype/llm.py`

## Behavior

The existing Study Guide now supports two paths:

1. Local deterministic requests continue to use `vocogni_assistant.answer_request()`. Examples: profile, progress, mistakes, next step, course list, and navigation.
2. Unhandled open-ended questions are passed to the LLM engine only when the provider is configured and the learner has enabled the session-only opt-in control.

The UI is currently rendered in the Browse/Learn flow, matching the previous assistant placement.

## Configuration

Use either server environment variables:

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

The endpoint must implement the OpenAI-compatible Chat Completions contract. No provider or credentials are bundled with the repository.

## Request data

When AI is enabled, the provider receives the current prompt, up to eight recent conversation messages, and a limited summary containing only selected learning preferences/grade level, course accuracy, and recent mistake tags.

The context builder deliberately excludes name, email, account ID, age, country, saved notes, and milestones. It does not prevent a learner from typing personal data into the chat itself.

## Safety and product boundaries

- AI is off by default; opt-in is session-only.
- Local account commands do not require external AI.
- API credentials remain server-side.
- The UI discloses the data sent and warns against entering sensitive information.
- Model output is labelled AI-generated.
- LLM output is not used for answer checking, scoring, or final mastery decisions.
- The engine prompt treats learner content as untrusted data and asks the model not to invent evidence.
- Provider retention/training terms and data location depend on the configured provider.
- The prototype does not implement verified parental consent, human moderation, incident reporting, or a child-safety compliance workflow.

## Known limitations

- Only OpenAI-compatible chat-completions providers are supported by this adapter.
- No streaming response, tool calling, multimodal input, embeddings, retrieval, fine-tuning, or model fallback chain.
- The model may hallucinate, misunderstand notation, or generate incorrect academic explanations.
- The learning summary uses existing aggregate progress and mistake tags; it is not LPM and cannot reliably infer a specific misconception.
- The progress summary and lesson diagnostic engines remain deterministic/rule-based.
- No production provider call, Streamlit deployment, or educational-quality evaluation has been verified in this change.

## Acceptance checks

- Local Study Guide commands still work with no provider configured.
- AI opt-in is unavailable when provider configuration is incomplete.
- Open-ended prompts call the provider only after opt-in.
- The prompt contains only the limited context builder output and bounded chat history.
- The assistant falls back when provider calls fail.
- API keys are not rendered or persisted in learner state.
- Existing Auth0, Supabase, progress JSONB, and answer-checking paths remain unchanged.
