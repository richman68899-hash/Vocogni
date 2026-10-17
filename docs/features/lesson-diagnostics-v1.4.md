# Vocogni v1.4 — Lesson Diagnostics and Adaptive Entry

**Status:** Unreleased; code added to a feature branch; integrated tests pending  
**Owner:** Vocogni project maintainer  
**Change ID:** VCG-FEAT-DIAGNOSTICS-001

## Problem
Lessons did not reliably establish a learner's starting point. Without a baseline, the prototype could not clearly expose missing prerequisites, recommend an appropriate starting pathway, or display a saved before/after practice checkpoint.

## Implemented scope
- Reusable five-item diagnostic schema and validation in `diagnostics.py`.
- Initial diagnostic content for three foundation lessons:
  - Simple Fractions — Understanding Fractions.
  - Algebra Basics — What Is a Variable?
  - Word Problems — Translating Words into Math.
- Score, prerequisite check, named skill weaknesses, answer explanations, placement rationale, and next-step recommendation.
- Five possible routes: prerequisite review, Level 1 (Easy), Level 2 (Medium), Level 3 (Hard), or a real-life project.
- One saved diagnostic result per learner/course/lesson ID. Existing result is shown on revisit; the diagnostic is not submitted again.
- Separate persistence for diagnostic scores and post-lesson practice checkpoint records.
- Progress-page display of diagnostics completed, baseline scores, post-lesson practice scores, and flagged skill areas.
- Versioned diagnostic configuration and acceptance tests for future lesson authors.

## Placement rule (explicit prototype heuristic)
1. If the prerequisite item is incorrect, recommend prerequisite review regardless of total score.
2. If the prerequisite item is correct: 1–2/5 routes to Level 1 (Easy); 3/5 routes to Level 2 (Medium); 4/5 routes to Level 3 (Hard); 5/5 routes to the real-life project.
3. Incorrect answers are mapped to their author-defined `skill_tag`. The engine lists those tags and the explanation/review action.
4. This is transparent rule-based logic (“AI-style decision support”), **not** a trained AI model or a validated psychometric instrument. Thresholds are initial hypotheses to evaluate.

## Architecture and persistence
- `data.py`: lesson-authored diagnostic question sets and pathways.
- `diagnostics.py`: schema validator, scorer, placement rule, weakness report, and pathway question selection.
- `sections/course.py`: one-time diagnostic form, result screen, adaptive lesson route, and post-lesson checkpoint.
- `state.py` and `logic.py`: separate durable diagnostic and lesson-assessment fields.
- `sections/progress.py`: learner-facing tracking and descriptive comparison.

Diagnostic items are kept separate from ordinary practice question counts/accuracy. The saved result is stored in the existing learner progress JSON payload; no Supabase table/schema change is intended.

## Limitations and interpretation
- Diagnostics are currently added to three initial lessons only; the reusable schema is intended for future lesson authors.
- Placement thresholds have not been validated with real learners.
- The post-lesson checkpoint uses lesson practice questions, not an equivalent standardized post-test. A percentage-point difference is descriptive and must not be reported as proven learning gain.
- Five selected-response items provide a coarse starting-point signal, not a comprehensive profile of ability.
- Existing learners who completed one of these lessons before v1.4 are not forced to complete a new diagnostic on review.
- The diagnostic is not a generative AI system and does not call an external model.

## Acceptance criteria
- [ ] All configured diagnostics pass schema validation.
- [ ] Each diagnostic requires all five answers and saves exactly one result.
- [ ] Reopening a lesson never lets a learner retake the submitted diagnostic.
- [ ] The prerequisite-failure override behaves as documented.
- [ ] Scores 2/5, 3/5, 4/5, and 5/5 with prerequisite correct route to Levels 1, 2, 3, and Project respectively.
- [ ] Each incorrect item adds the correct skill tag to the weakness report.
- [ ] Diagnostic scores do not increase ordinary practice-question or mistake totals.
- [ ] Diagnostic results survive refresh and re-login.
- [ ] Starting routes and post-lesson checkpoints persist.
- [ ] Prior progress records missing the new keys continue to load.
- [ ] No two accounts share diagnostic data.
- [ ] A live UI pass confirms that the form, route screens, hints, and progress page work on mobile and desktop.
- [ ] Test records, commit SHA, and deployment result are recorded before release.

## Evidence to collect
- Screenshot of the diagnostic form.
- Screenshot of a result including score, weakness tag, placement explanation, and route.
- Progress-page screenshot showing baseline and post-lesson checkpoint.
- Automated test output and integrated deployment acceptance results.
- A note identifying the tested commit SHA and date.

## Release decision
Keep the change under **Unreleased** until the acceptance list is complete. Provisionally classify it as a minor feature release (v1.4.0) only when tests pass and the pull request is merged. Do not call its recommendation “AI diagnosis” in public product claims without clarifying that it is rule-based prototype logic.
