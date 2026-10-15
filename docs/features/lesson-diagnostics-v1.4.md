# VOCogni v1.4 — Lesson Diagnostics and Adaptive Entry

**Status:** Unreleased; code added to a feature branch; integrated tests pending  
**Owner:** VOCogni project maintainer  
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
- Five diagnostic outcomes that unlock cumulative sets of practice tests: Level 1 only, Levels 1–2, Levels 1–3, or all three levels plus a real-life project. A prerequisite miss gates access to Level 1 until foundations are reviewed.
- One saved diagnostic result per learner/course/lesson ID. Existing result is shown on revisit; the diagnostic is not submitted again.
- Separate persistence for diagnostic scores and post-lesson practice checkpoint records.
- Progress-page display of diagnostics completed, baseline scores, post-lesson practice scores, and flagged skill areas.
- Versioned diagnostic configuration and acceptance tests for future lesson authors.

## Placement rule (explicit prototype heuristic)
1. The diagnostic is the first test shown in a configured lesson and is labelled **Test 1 — Diagnostic**. It can be submitted once per learner per lesson.
2. If the prerequisite item is incorrect, only Level 1 is unlocked while the learner reviews the prerequisite.
3. If the prerequisite item is correct: 1–2/5 unlocks Level 1 (Easy); 3/5 unlocks Levels 1–2; 4/5 unlocks Levels 1–3; 5/5 unlocks Levels 1–3 and the real-life project.
4. Practice tests can be repeated. Retaking practice creates a fresh attempt and never resets or reopens the diagnostic.
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
- Practice attempt history is not yet a full longitudinal assessment record; the current checkpoint is descriptive and should not be treated as a validated gain measure.
- The diagnostic is not a generative AI system and does not call an external model.

## Acceptance criteria
- [ ] All configured diagnostics pass schema validation.
- [ ] Each diagnostic requires all five answers and saves exactly one result.
- [ ] Reopening a lesson never lets a learner retake the submitted diagnostic.
- [ ] The prerequisite-failure override behaves as documented.
- [ ] Scores 2/5, 3/5, 4/5, and 5/5 with prerequisite correct unlock Level 1; Levels 1–2; Levels 1–3; and Levels 1–3 plus Project, respectively.
- [ ] The diagnostic appears first and is labelled Test 1 — Diagnostic.
- [ ] Practice tests can be repeated with fresh answer-widget state.
- [ ] A repeated practice test does not expose a diagnostic retake.
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
