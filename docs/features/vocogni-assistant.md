# Vocogni Assistant — first implementation

## Purpose

A floating support panel available throughout the Learn/Browse flow, including course and lesson screens. It reads the authenticated learner's in-memory profile, progress, settings, notes, milestones, and existing practice history.

## Supported instructions

- Summarise my profile
- Show my latest mistakes
- Summarise my progress / how am I doing
- Recommend my next step
- List available courses
- Summarise my notes / milestones
- Show my learning settings
- Open Profile, Progress, Learn, Notes, or Settings
- Help / supported requests

The intent handler is deterministic and framework-free. Unsupported requests receive a clear explanation instead of fabricated answers. It does not call a hosted AI model or send profile/progress data to a third-party API in this version.

## Data boundaries

- The conversation is kept in Streamlit session state and is not added to the durable learner-state bundle.
- Learner records are not mutated by asking questions.
- "Latest mistakes" uses saved practice attempt result records and their timestamps when available.
- Where only aggregate mistake counters exist, the assistant labels them as frequent themes rather than claiming they are the latest.
- Recommendations reuse Vocogni's current rule-based coach/recommendation functions. They are not described as validated learning diagnoses.

## Interface

A fixed bottom-right launcher opens a bounded-height responsive panel. Conversation display is limited to the latest eight messages; the current session retains at most twenty message records. A sticky **Suggested prompts** area keeps the four quick actions visible throughout the conversation, not only before the first message.

## Future LLM integration

A generative model should be added behind the pure `answer_request` interface only after choosing a provider, configuring secrets outside source control, defining data-sharing disclosure/consent, and keeping deterministic fallbacks for profile and history requests. Do not place API keys in code or send more learner data than the specific request needs.
