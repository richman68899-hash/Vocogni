# Skill confirmation for provisional diagnostic signals

**Status:** Implemented in source; hosted UI validation remains outstanding.

## Learner flow

When Learning Intelligence flags a skill from only one baseline diagnostic item, the learner can request one additional question for that same skill. Vocogni selects from the current Verified Question Engine registry, limited to the same course and skill, and to multiple-choice/numeric response types. It may use a reviewed conceptual or applied item; the learner is not restricted to a particular question purpose. Question IDs already used in saved diagnostic or verified practice evidence are excluded.

If no unused verified item exists for that skill, Vocogni explains the content-bank limitation. It does not repeat an item or fall back to an unreviewed legacy question.

## Recording and interpretation

A submitted check is revalidated against the current VQE before it is recorded. The result is stored in the separate `skill_confirmation_attempts` list within the existing learner-progress JSON. Only the selected question ID, source lesson, verified skill provenance, correctness, score, and timestamp are stored; the raw response is not retained by this feature.

Confirmation results strengthen the diagnostic evidence set but do not increase ordinary practice accuracy or the six-answer skill-trajectory window. A distinct second item can remove the single-item provisional label, but two answers are still a small sample and do not prove mastery or a stable misconception.

## Compatibility and safeguards

The field is additive to existing course progress. Older learners default to an empty confirmation list. Malformed legacy values are sanitised on restore. A question that no longer passes current VQE verification is rejected at submit time.
