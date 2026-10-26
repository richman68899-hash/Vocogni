# Question-attempt provenance contract

**Status:** First Phase 0 contract implementation  
**Scope:** Additive provenance fields for newly recorded question-answer results  
**Authority:** `question_engine.py` / VQE provides question metadata; this contract checks record shape only.

## Why this exists

## Scope of this increment

This first slice is wired into the core course lesson-practice result path through `sections/course.py`. The Revision Sprint and Coach currently record attempts through separate existing paths; they are intentionally left unchanged here and should adopt the contract in follow-up increments after their generated-question and source-question semantics are reconciled.

New answers are used by practice history, the revision sprint, coaching and the Mastery Receipt. These consumers need a consistent record of *which question version was answered* and what review/skill context was attached at the time. Without a versioned shared shape, later content edits can make old evidence ambiguous.

## Contract version 1

Every new provenance payload returned by `question_engine.attempt_metadata()` contains:

| Field | Meaning | Rule |
|---|---|---|
| `provenance_schema_version` | Version of this metadata shape | Required positive supported version; currently `1` |
| `question_id` | Stable ID of the question presented | Required, non-empty |
| `course_id` | Course context at attempt time | Optional non-empty string |
| `lesson_id` | Lesson context at attempt time | Optional non-empty string |
| `question_version` | Version of question content represented by VQE | Required positive integer |
| `skill_id` | Stable skill identifier where known | Optional; display labels are not substitutes |
| `question_purpose` | Purpose assigned to the question | Optional |
| `verification_status` | VQE review status at attempt time | One of `legacy`, `needs_review`, `verified`, `retired` |
| `verification_engine_version` | VQE version that supplied the status | Optional for legacy/global callers; populated by VQE |
| `question_source_field` | Authored field containing the question | Optional provenance for debugging/review |

The contract is structural; it does **not** decide whether a question is mathematically or pedagogically correct. VQE is the only authority for question verification. Graders remain authoritative for scoring.

## Compatibility and persistence

- Fields are additive to new answer-result dictionaries.
- Existing progress JSON and historical results are not rewritten or migrated.
- Readers must tolerate older results without these fields.
- This step does not add a database table, change Supabase, or create a second persistence path.
- The payload does not include answer text, raw notes, source documents, prompts, or other private learner content.
- A new provenance version should be introduced only with a compatibility plan and tests for old records.

## Acceptance criteria

- [x] Registered questions receive a versioned provenance payload.
- [x] Missing/unregistered questions remain explicitly `legacy`; they are not promoted to verified.
- [x] Schema validation catches malformed metadata without re-verifying the question.
- [x] Existing attempt history can still be read by the Mastery Receipt.
- [x] Unit tests are framework-free and use no secrets or database.
- [x] Full Python test workflow passes on the PR (run 40283200949).
- [ ] Hosted lesson/practice flow and signed-in save/reload are manually smoke-tested.

## Limits

This establishes a consistent question-provenance shape for new records; it does not yet normalize every historical result or establish a universal schema for all activity types. Live Streamlit/Supabase behavior remains separate verification.
