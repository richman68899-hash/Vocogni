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

The local intent handler is deterministic and framework-free. Supported account-data commands use the saved learner data passed to the Study Guide. Open-ended subject tutoring can use the configured external AI provider only after explicit session-only opt-in; it is off by default. When enabled, the current message, up to eight prior AI-tutoring messages, and a limited learning summary may be sent to that provider.

## Data boundaries

- The conversation is kept in Streamlit session state and is not added to the durable learner-state bundle.
- Learner records are not mutated by asking questions.
- "Latest mistakes" uses saved practice attempt result records and their timestamps when available.
- Where only aggregate mistake counters exist, the assistant labels them as frequent themes rather than claiming they are the latest.
- Recommendations reuse Vocogni's current rule-based coach/recommendation functions. They are not described as validated learning diagnoses.

## Interface

The sidebar Study Guide launcher opens the active responsive assistant panel. Conversation display is limited to the latest eight messages; the current session retains at most twenty message records. Four account-data shortcuts appear above the conversation and remain sticky while the page scrolls, so they can be used before or after the first message.

## Optional AI tutoring

Configure the OpenAI-compatible provider through Streamlit secrets or environment variables, never source control. Keep session opt-in explicit and off by default, explain the provider data flow before enabling it, retain deterministic local fallbacks for profile and history requests, and send no more learner data than the documented limited context. Provider retention and training terms depend on the selected provider.
