# Question-attempt provenance contract

**Status:** Phase 0 cross-path contract implementation  
**Scope:** Additive provenance fields for newly recorded question-answer results  
**Authority:** `question_engine.py` / VQE provides question metadata; this contract checks record shape only.

## Why this exists

## Scope of this increment

This increment wires the same versioned contract into the core course lesson-practice path (`sections/course.py`), the framework-free Revision Sprint recorder (`revision_sprint.py`), and Coach (`coach.py`). Coach keeps stable source identity separate from the rendered instance so a generated variant cannot be mistaken for the authored source question.

New answers are used by practice history, the revision sprint, coaching and the Mastery Receipt. These consumers need a consistent record of *which question version was answered* and what review/skill context was attached at the time. Without a versioned shared shape, later content edits can make old evidence ambiguous.

## Contract version 1

Every new provenance payload returned by `question_engine.attempt_metadata()` contains:

| Field | Meaning | Rule |
|---|---|---|
| `provenance_schema_version` | Version of this metadata shape | Required positive supported version; currently `1` |
| `question_id` | Stable ID of the canonical/source question whose provenance is recorded | Required, non-empty; derived presentations retain this source ID |
| `course_id` | Course context at attempt time | Optional non-empty string |
| `lesson_id` | Lesson context at attempt time | Optional non-empty string |
| `question_version` | Version of question content represented by VQE | Required positive integer |
| `skill_id` | Stable skill identifier where known | Optional; display labels are not substitutes |
| `question_purpose` | Purpose assigned to the question | Optional |
| `verification_status` | VQE review status at attempt time | One of `legacy`, `needs_review`, `verified`, `retired` |
| `verification_engine_version` | VQE version that supplied the status | Optional for legacy/global callers; populated by VQE |
| `question_source_field` | Authored field containing the question | Optional provenance for debugging/review |

Some consumers may add presentation fields without changing the shared contract:

| Extension field | Meaning | Rule |
|---|---|---|
| `presented_question_id` | ID of the item instance actually shown in the UI | Used when the rendered item has a different ID from its stable source |
| `question_origin` | How the presented item relates to the source | For Coach this is `authored_option_shuffle`, `authored_reuse`, or `generated_template` |

For Coach, the source question stays in `question_id` and the rendered instance is stored as `presented_question_id`. Authored questions with shuffled multiple-choice option order retain the source verification status. A generated question with changed content is recorded as `needs_review`, never as `verified`; a retired source remains `retired`.

The contract is structural; it does **not** decide whether a question is mathematically or pedagogically correct. VQE is the only authority for question verification. Graders remain authoritative for scoring.

## Compatibility and persistence

- Fields are additive to new answer-result dictionaries.
- Existing progress JSON and historical results are not rewritten or migrated.
- Readers must tolerate older results without these fields.
- This step does not add a database table, change Supabase, or create a second persistence path.
- The payload does not include answer text, raw notes, source documents, prompts, or other private learner content.
- A new provenance version should be introduced only with a compatibility plan and tests for old records.

## Acceptance criteria

- [x] Registered questions receive a versioned provenance payload in ordinary lesson practice and Revision Sprint.
- [x] Missing/unregistered questions remain explicitly `legacy`; they are not promoted to verified.
- [x] Coach stores the common contract plus separate source and presented-question IDs.
- [x] Materially changed generated Coach variants are downgraded to `needs_review`; retired sources are never promoted.
- [x] Schema validation catches malformed metadata without re-verifying the question.
- [x] Existing attempt history can still be read by the Mastery Receipt; historical records are not rewritten.
- [x] Unit tests are framework-free and use no secrets or database.
- [ ] CI on this increment must pass before merge.
- [ ] Hosted lesson/practice, Coach, Revision Sprint, and signed-in save/reload are manually smoke-tested.

## Limits

This establishes a consistent question-provenance shape for new records; it does not yet normalize every historical result or establish a universal schema for all activity types. Live Streamlit/Supabase behavior remains separate verification.
