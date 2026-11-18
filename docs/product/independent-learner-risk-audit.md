# Independent Grade 7–9 Learner Audit

**Status:** Source-based product audit; live usability and learning outcomes remain unverified.
**Audience:** A learner using Vocogni without a teacher or tutor present.
**Decision:** Do not describe the current prototype as ready for unsupervised public use.

## Executive finding

Vocogni has a credible learning architecture, but the repository does not yet establish that a learner can reliably recover from confusion, distinguish weak evidence from mastery, or obtain help when the system or content fails. Technical completion is not equivalent to independent learning success.

This audit separates observed repository facts from product risks that require live validation.

## Prioritized problems

### P0 — Child-safety, privacy, and operational readiness

**Observed**
- The README says the prototype is not production-validated.
- The Stage 1 beta checklist explicitly requires a responsible adult operator, age/guardian-consent review, child-safety risk assessment, monitored support/reporting, retention/deletion procedures, and device/network testing before a real learner pilot.
- The launch-readiness document says legal drafts are not proof of compliance and that operator/contact details, final legal review, consent implementation, retention/deletion and incident response remain to be verified.
- The README says no real learner data should be used until privacy, provider review, access controls, retention/deletion, and applicable legal requirements are addressed.

**Learner consequence**
A student may encounter a harmful, confusing, privacy-sensitive, or technically broken situation without a defined, monitored route to a responsible human.

**Required resolution**
Treat supervised-only operation as a hard release constraint until the responsible operator completes the documented gates. Do not solve this with a decorative disclaimer or an unmonitored contact link.

**Acceptance**
- A named responsible adult operator and monitored support/safety channel exist.
- The deployed data flow, provider terms, consent process, retention/deletion, and incident response have been reviewed and tested.
- A learner-facing route to report a problem is available and monitored.
- No public or unsupervised cohort is enabled before sign-off.

### P1 — Learner recovery when confused or stuck

**Observed**
- The core lesson flow has intro, question, feedback and completion stages.
- Lessons contain explanations, worked examples and question feedback, but the repository's existence of these elements does not prove that they are sufficient for a struggling learner.
- The app has an optional Study Guide; external AI tutoring is off by default and separate from deterministic grading.

**Risk / inference**
A learner who does not understand an explanation may repeatedly guess, copy a worked example without understanding it, or leave the lesson. A generic chatbot is not a reliable substitute for a structured recovery path.

**Required resolution**
For every supported skill, provide a deterministic help ladder:
1. Restate the learning objective in plain language.
2. Show a smaller prerequisite example.
3. Reveal a worked example one step at a time.
4. Give a near-transfer practice question.
5. Explain the specific error after an attempt.
6. Offer a clear retry, review, or human-help route.

**Acceptance**
- A learner can access help from the exact point of confusion without losing their answer or progress.
- Each help step is linked to the target skill and does not reveal the answer prematurely.
- If no verified support exists, say so and offer a safe exit rather than inventing content.
- The flow works with the external AI provider unavailable.

### P1 — Overconfident diagnosis and mastery claims

**Observed**
- The diagnostic engine is explicitly rule-based, not a trained model or validated psychometric assessment.
- A diagnostic uses five items, and the acceptance plan says a single missed skill is a preliminary signal requiring a distinct confirmation question.
- The README says delayed-retention checks and validated learning-effectiveness measurements are not implemented.
- The Progress page's intervention links are described as descriptive sequencing, not causal evidence that a support worked.

**Learner consequence**
A student may interpret one short check, one correct answer, or a progress percentage as proof of mastery or as a fixed judgement of ability.

**Required resolution**
- Label placement as a provisional starting recommendation, not a verdict.
- Require independent, varied evidence before promoting a skill to a stronger mastery state.
- Distinguish diagnostic, supported practice, independent practice, transfer, and delayed-retention evidence.
- Show sample size and evidence recency beside conclusions.
- Never imply that a streak, completion percentage, or one assessment measures intelligence.

**Acceptance**
- One response cannot create a confirmed misconception or mastery claim.
- Mastery language is tied to explicit evidence thresholds and question provenance.
- Missing/insufficient evidence is shown as "not enough evidence", not silently converted to a score.

### P1 — Content coverage and correctness are not yet a complete product

**Observed**
- The repository contains a small seed course catalogue and a verified-question registry.
- VQE documentation says unreviewed/legacy content must not be presented as verified.
- The Stage 1 checklist requires independent review of every pilot answer key, tolerance, explanation, distractor, grade-band label and transfer question.

**Learner consequence**
A learner can follow a polished pathway but encounter gaps, inconsistent difficulty, ambiguous wording, or an incorrect explanation.

**Required resolution**
- Publish only courses with a complete reviewed learning path.
- Make content coverage and verification status visible internally.
- Add automated structural checks for missing explanations, malformed answers, duplicate IDs, unsupported question types, and missing skill links.
- Keep unreviewed content out of verified-only learner flows.

**Acceptance**
- Every pilot lesson has a reviewed objective, explanation, worked example, practice set, answer key and feedback.
- Every question has stable identity, skill mapping, version/provenance and a review status.
- No course is represented as complete when required stages are missing.

### P1 — Weak evidence of independent usability

**Observed**
- The Stage 1 checklist requires real-device tests on Android, iPhone, desktop, tablet and a narrow viewport, plus slow/unstable network checks.
- The README explicitly says automated tests do not validate actual-device usability or educational effectiveness.

**Learner consequence**
A learner may not find the next action, understand navigation, recover after refresh, or know whether an answer was saved.

**Required resolution**
Run moderated usability tests with representative Grade 7–9 learners using realistic tasks, then fix observed failure points before adding engagement features.

**Acceptance**
- Learners can complete first-use onboarding, choose a course, understand a lesson, submit and interpret feedback, resume after leaving, and find help without coaching.
- Record task completion, time-to-first-success, unassisted recovery, abandonment point and learner-reported confusion.
- Test accessibility, keyboard navigation, readable math notation and mobile controls.

### P2 — Progress and next-step recommendations need better calibration

**Observed**
- Vocogni already has mistake tracking, recommendations, progress summaries and intervention records.
- The repository explicitly distinguishes recorded exposure from evidence that the exposure caused improvement.

**Risk / inference**
A recommendation can feel authoritative even when based on sparse, stale, or narrow evidence.

**Required resolution**
Show why a recommendation was made, which attempts support it, how recent the evidence is, and what the learner can do if it seems wrong. Avoid turning sparse data into deterministic labels.

### P2 — Engagement mechanics can displace learning

**Risk / inference**
Streaks, coins, gardens and completion percentages can increase return visits without proving learning. For Grade 7–9 learners, avoid shame, streak-loss pressure, or reward systems that encourage low-quality repetition.

**Required resolution**
Reward meaningful learning activity and reflection, not app opens or raw time. Make rest days neutral. Keep learning outcomes more prominent than cosmetic rewards.

## Recommended implementation order

1. **Release/safeguarding gate:** establish the responsible operator, monitored support, consent/privacy review, retention/deletion and incident response before any unsupervised cohort.
2. **Independent recovery path:** deterministic, skill-linked help and a clear human-escalation route.
3. **Evidence calibration:** provisional diagnostics, explicit evidence categories, and defensible mastery thresholds.
4. **Content quality gate:** verified-only pilot content and automated structural validation.
5. **Learner usability evidence:** observe real Grade 7–9 learners on actual devices and fix the highest-frequency blockers.
6. **Recommendation and engagement calibration:** only after the learning journey is reliable.

## Scope and evidence limits

This is a source review, not a live black-box test. It does not establish that every listed risk currently occurs. Items marked "risk / inference" require learner observation or runtime testing. The existing acceptance documents should remain the authority for recording test evidence. Do not mark a gate complete from code presence alone.
