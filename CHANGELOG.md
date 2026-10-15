# Changelog

All notable VOCogni changes are recorded here. Features remain under `Unreleased` until their acceptance tests are complete, the pull request is merged, and a release tag is created.

## [Unreleased] — Lesson diagnostics (proposed v1.4.0)

### Added
- Reusable and structurally validated five-question lesson diagnostic schema.
- Rule-based cumulative unlocking of practice levels based on the diagnostic score, with a prerequisite gate.
- Initial diagnostics for Understanding Fractions, What Is a Variable?, and Translating Words into Math.
- Skill-tagged weakness reporting, answer explanations, and placement rationale.
- One-time durable diagnostic records and a separate post-lesson practice checkpoint.
- Progress dashboard measures for completed diagnostics, baseline results, post-lesson practice, and flagged weaknesses.
- Automated rule-engine tests and acceptance-test plan.

### Changed
- The diagnostic is the first test in a configured lesson and is labelled Test 1 — Diagnostic.
- Diagnostic outcomes unlock sets of levels rather than prescribing one mandatory level.
- Practice tests can be repeated with fresh answer state; diagnostic results remain one-time.
- Diagnostic items are recorded separately from normal practice counts.

### Notes
- The placement engine is transparent rule-based prototype logic, not a trained AI model.
- The diagnostic and post-lesson practice sets are not equivalent standardized assessments; their score difference must not be represented as proven learning gain.
- Only three initial lessons currently have diagnostic content. The engine/schema are reusable for adding future lesson diagnostics.
- Release is pending automated and integrated deployment testing.
