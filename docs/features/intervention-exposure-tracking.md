# Teaching-support exposure and follow-up evidence

**Status:** Implemented in the application code; live learner validation remains outstanding.

## What is recorded

The lesson flow appends an event when a learner advances past the concept explanation, advances past the worked example, explicitly reveals a hint (or is shown an automatic hint), sees item feedback, or is shown a targeted repair cue.

Each event stores only:
- a stable event ID for deduplication;
- support type and display label;
- course and lesson IDs;
- a VQE-verified skill ID and question ID when available;
- practice-attempt number and timestamp.

Raw answers, question prompts, notes, and assistant messages are not copied into the support ledger. Events are added to the existing per-learner progress JSON; no new table or database migration is required.

## How follow-up is calculated

For each support event, Vocogni looks for up to the next three later practice answers in the same course and verified skill. It re-resolves each question against the current Verified Question Engine registry and requires the answer's per-item answered_at timestamp to be later than the support event. Older answer records without that timestamp are intentionally not matched.

The report shows the observed accuracy among those later answers. It does not claim that a support caused improvement: several supports may precede the same answers, the questions are not controlled equivalents, and the student may receive other instruction. It is not a validated measure of retention or transfer.

## Privacy and compatibility

The event ledger is additive to the existing progress JSON and is capped at 300 support events per course. Existing learner records remain readable. The feature does not store raw written work or additional identity fields.

## Validation required before use

Automated tests cover event idempotency, validation, provenance checks, time ordering, and legacy-state non-mutation. The actual deployed app still needs a supervised synthetic-account smoke test for concept/example navigation, hint display, feedback display, save/reload, phone layout, and failed-save recovery. Educational claims require separate teacher review and real pilot evidence after all learner-protection gates are complete.
