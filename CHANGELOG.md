# Changelog

- Add an optional saved gender preference to the learner profile for future personalization.
- Show the current development version in small, muted text at the bottom-left of Settings.
- Standardize the product name to “Vocogni” in app copy, comments, and documentation.

- Extend the diagnostic-first three-screen lesson flow to Simple Fractions and Algebra Basics.
- Persist lesson screen checkpoints in existing learner progress records so learners can resume after refresh or re-login.
- Preserve existing lesson IDs, completed-lesson history, diagnostic results, attempts, and aggregate scores.


## Unreleased
- Add a separate first-item diagnostic to the Word Problems course while retaining the four learning lessons.
- Give each Word Problems lesson a three-screen concept → worked example → interactive question flow.
- Count the course diagnostic in Word Problems progress and add structural regression tests.


All notable Vocogni changes are recorded here. Features remain under `Unreleased` until their acceptance tests are complete, the pull request is merged, and a release tag is created.

## [Unreleased] — Lesson flow rebuild and diagnostic-gated practice

### Added
- Reusable and structurally validated five-question lesson diagnostic schema.
- Rule-based placement into prerequisite review, Level 1 (Easy), Level 2 (Medium), Level 3 (Hard), or a real-life project.
- Initial diagnostics for Understanding Fractions, What Is a Variable?, and Translating Words into Math.
- Skill-tagged weakness reporting, answer explanations, and placement rationale.
- One-time durable diagnostic records and a separate post-lesson practice checkpoint.
- Progress dashboard measures for completed diagnostics, baseline results, post-lesson practice, and flagged weaknesses.
- Automated rule-engine tests and acceptance-test plan.

### Changed
- The one-time diagnostic is the first assessment for each configured lesson.
- Diagnostic results expose cumulative unlocked practice routes; prerequisite failure gates the learner to Level 1.
- Learners can select any unlocked practice route; the chosen route is saved and remains fixed after selection.
- Rebuilt the lesson landing screen as a stable hub derived from durable diagnostic records.
- Stored practice-attempt summaries separately from the one-time diagnostic and legacy lesson-completion list.
- Allowed completed lessons to reopen at the hub and start another practice attempt without resetting diagnostic data.
- Added explicit attempt-complete and return-to-hub transitions to avoid completion rerun loops.
- Diagnostic items are recorded separately from normal practice counts.

### Notes
- The placement engine is transparent rule-based prototype logic, not a trained AI model.
- The diagnostic and post-lesson practice sets are not equivalent standardized assessments; their score difference must not be represented as proven learning gain.
- Only three initial lessons currently have diagnostic content. The engine/schema are reusable for adding future lesson diagnostics.
- Release is pending automated and integrated deployment testing.
