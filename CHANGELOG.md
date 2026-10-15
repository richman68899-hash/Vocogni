# Changelog

All notable VOCogni changes are recorded here. Features remain under `Unreleased` until their acceptance tests are complete, the pull request is merged, and a release tag is created.

## [Unreleased] — Diagnostic unlocks and practice retakes

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
- Practice tests are intended to be repeatable without allowing a diagnostic retake.
- Diagnostic items are recorded separately from normal practice counts.

### Notes
- The placement engine is transparent rule-based prototype logic, not a trained AI model.
- The diagnostic and post-lesson practice sets are not equivalent standardized assessments; their score difference must not be represented as proven learning gain.
- Only three initial lessons currently have diagnostic content. The engine/schema are reusable for adding future lesson diagnostics.
- Release is pending automated and integrated deployment testing.
