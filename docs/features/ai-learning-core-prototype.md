# AI Learning Core — Experimental Prototype

**Branch:** `feature/ai-learning-core-prototype`  
**Status:** isolated experiment; not integrated into the deployed application.

## Scope

This prototype explores two separate capabilities:

1. **Natural-language generation:** an optional OpenAI-compatible chat-completions adapter for explanations and conversational learning support.
2. **Learning-pattern recognition:** transparent heuristics that identify explicit text signals in incorrect attempts (sign handling, inverse operations, equality balance, fraction denominators, distribution, and keyword-based reasoning).

The pattern recognizer is deterministic and explainable. It is not machine learning, does not infer a learner's mental state, and does not establish a misconception. Repeated matches are only signals for review.

## Architecture

- `ai_prototype/llm.py`: optional provider adapter, configured only through environment variables.
- `ai_prototype/patterns.py`: pure Python pattern rules and attempt aggregation.
- `ai_prototype/engine.py`: prompt orchestration, evidence-limited context, and deterministic fallback.
- `ai_lab_app.py`: standalone Streamlit sandbox; production `app.py` is unchanged.
- `tests/test_ai_prototype.py`: offline tests for the deterministic layer and fallback behavior.

## Run

```bash
pip install -r requirements.txt
streamlit run ai_lab_app.py
python -m unittest discover -s tests -p 'test_ai_prototype.py' -v
```

Configure a compatible provider before expecting generated responses:

- `VOCogni_LLM_BASE_URL`
- `VOCogni_LLM_MODEL`
- `VOCogni_LLM_API_KEY`

The prototype does not select a provider, create credentials, or include API keys. With no configuration, it uses a deterministic fallback.

## Data and safety boundaries

- The sandbox is not connected to Auth0, Supabase, or production learner records.
- Conversation state exists only in the Streamlit session.
- Do not enter real learner identifiers, private notes, passwords, contact details, or sensitive data.
- When enabled, user prompts and bounded conversation history are sent to the configured model provider. Review provider retention, training, data location, consent, and age-related requirements before any real learner use.
- Pattern reports must be presented as heuristic evidence, not validated diagnoses or mastery scores.

## Acceptance criteria

- The production entrypoint and existing learner-state schema remain unchanged.
- The sandbox starts independently.
- Pattern rules return explicit evidence counts and uncertainty language.
- LLM configuration is external to source control.
- Missing provider configuration or request failure does not crash the learning flow.
- Offline unit tests cover pattern recognition and deterministic fallback.

## Not included

No embeddings, vector database, fine-tuning, model training, image/OCR understanding, long-term memory, autonomous actions, or validated adaptive learning model. Those should be separate experiments justified by learner evidence.
