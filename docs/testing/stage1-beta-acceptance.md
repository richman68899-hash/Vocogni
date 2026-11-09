# Stage 1 Beta Acceptance — Evidence Checklist

**Purpose:** Decide whether a specific Vocogni build is ready for a small, supervised, online learner pilot.

This checklist supplements (it does not replace) the detailed [lesson diagnostics acceptance tests](lesson-diagnostics-acceptance.md) and the [legal and safety launch-readiness checklist](../legal/launch-readiness.md).

A feature is not marked as passed solely because its code exists, a unit test passes, or the owner has used it once. Record the tested commit, environment, steps, result, and evidence. Use synthetic test accounts and synthetic learner data until the legal, consent, privacy, and safeguarding gates below have been reviewed and completed by the responsible adult operator.

## 1. Release identity and automated checks

Record before testing:

| Field | Evidence |
|---|---|
| Candidate branch and commit SHA | |
| Deployed URL / environment | |
| Deployed commit SHA or deployment identifier | |
| Test date and timezone | |
| Tester / responsible adult operator | |
| Test data | Synthetic only until the learner-protection gates are cleared |

Acceptance:

- [ ] Candidate code is merged to the intended release branch.
- [ ] The deployed build corresponds to the exact commit under test.
- [ ] The full GitHub Actions test suite passes on that commit.
- [ ] Python compilation checks pass.
- [ ] No unresolved P0 defect is open.
- [ ] The release can be rolled back to the last known-good build.

**Do not infer deployment freshness from a successful GitHub Actions run.** Verify the deployed commit independently.

## 2. Authentication and account boundaries

Use two separately created synthetic test accounts, A and B.

- [ ] A can sign in, reach the authenticated application, and sign out.
- [ ] B can sign in independently.
- [ ] A's profile, notes, settings, course progress, diagnostics, and attempts do not appear in B's session.
- [ ] Switching accounts in the same browser session does not retain the prior learner's state.
- [ ] Refreshing an authenticated session restores the correct learner's state.
- [ ] Expired or unauthenticated sessions cannot open learner pages or read learner records.
- [ ] Invalid or missing identity claims fail closed.
- [ ] Logout does not complete when the required final save fails.

Record the synthetic account labels used; never record passwords, tokens, or real personal data.

## 3. Persistence and recovery

Run these checks against a non-production test environment wherever failure injection is required.

- [ ] First login creates the expected learner record.
- [ ] Profile, settings, notes, notes folders, milestones, whiteboards, diagnostics, practice attempts, and course progress save and restore.
- [ ] A refresh and a sign-out/sign-in cycle restore the latest confirmed save.
- [ ] An unsuccessful database write is shown as an error, not as a successful save.
- [ ] Failed writes remain marked as pending/failed and can be retried.
- [ ] A successful retry clears the error and persists the expected state.
- [ ] A failed final save prevents logout and makes the retry action available.
- [ ] Older records with missing newer fields load without discarding existing learner data.
- [ ] Two sessions for the same account are checked for accidental stale-state overwrites; record any limitation found.

Do not simulate database outages or destructive changes against real learner records.

## 4. Complete learning journey

Run the journey for each course included in the pilot, using synthetic accounts until learner-protection gates are complete.

- [ ] Course discovery and course entry work.
- [ ] The diagnostic appears at the intended point in the journey.
- [ ] All required diagnostic inputs are accepted and unanswered submissions are handled safely.
- [ ] Each diagnostic route and prerequisite gate matches its documented rule.
- [ ] The learner can understand the concept explanation and worked example.
- [ ] Interactive answer inputs work on the selected devices.
- [ ] Correct and incorrect answers produce relevant, understandable feedback.
- [ ] Practice attempts are stored separately; retakes do not overwrite the original diagnostic.
- [ ] Independent application/transfer questions are selected where the course has verified coverage.
- [ ] Progress summaries distinguish diagnostic evidence, practice evidence, and independent application evidence.
- [ ] A learner can leave and resume without losing the last confirmed progress.

A correct software route is not proof that the diagnostic accurately identifies a learner's underlying misconception. Content and diagnostic validity require separate review and evidence from learners.

## 5. Mathematical content review

A qualified mathematics reviewer or appropriately experienced teacher should inspect the exact content included in the pilot.

- [ ] Every pilot question has an independently checked answer key.
- [ ] Numeric tolerances, accepted equivalent forms, units, and partial-credit rules are appropriate.
- [ ] Explanations and worked examples are mathematically correct.
- [ ] Distractors and misconception feedback are not misleading.
- [ ] Grade-band labels and difficulty classifications are reasonable for the intended cohort.
- [ ] Transfer questions assess the same intended skill in a meaningfully different context or representation.
- [ ] Unreviewed or legacy questions are not presented as verified content.

Record the reviewer, content version/commit, courses reviewed, and unresolved items.

## 6. Browser, device, and network checks

Test the actual deployed application on representative devices rather than relying only on responsive CSS checks.

| Environment | Tested | Notes / defect ID |
|---|---|---|
| Android phone + Chrome | [ ] | |
| iPhone + Safari | [ ] | |
| Desktop Chrome / Edge | [ ] | |
| Tablet-sized viewport | [ ] | |
| Narrow viewport around 360 px | [ ] | |
| Slow or unstable connection | [ ] | |

For every tested environment:

- [ ] No essential controls are clipped, hidden, or too difficult to activate.
- [ ] Mathematical notation, fractions, diagrams, and answer inputs remain readable.
- [ ] Navigation and back/refresh behavior are understandable.
- [ ] Loading and AI/provider failure states are understandable, where applicable.
- [ ] The app does not silently lose unsaved work when connectivity fails.
- [ ] Response and loading times are recorded against a threshold chosen before the pilot.

## 7. Privacy, consent, and learner safeguarding — release gate

**Do not invite real Grade 7–9 learners or collect their personal learning records until the responsible adult operator has reviewed and completed the applicable requirements.** This checklist is operational guidance, not legal advice.

- [ ] The responsible operator/controller and monitored contact details are established.
- [ ] Qualified counsel has reviewed the actual service, intended ages, jurisdictions, data flows, consent approach, and school/guardian responsibilities.
- [ ] Any required age-identification and parent/guardian consent process is implemented, tested, and recorded.
- [ ] The final privacy notice and terms match the deployed product and providers.
- [ ] Provider terms, data location, subprocessors, retention, and cross-border processing are reviewed.
- [ ] Data minimisation, access controls, retention, deletion, and privacy-request handling are implemented.
- [ ] A monitored support and safety-reporting channel is available.
- [ ] A child-safety risk assessment and incident-response procedure are complete.
- [ ] Any external AI feature used by the cohort has a separately reviewed provider/data-flow/safety decision; AI tutoring remains off unless explicitly approved.

A checkbox, draft policy, invitation-only link, or verbal assurance is not a substitute for a legally valid consent process where one is required.

## 8. Pilot sign-off

Complete one row per test case or evidence item. Keep the evidence link in a private, access-controlled location and do not attach real learner data to public GitHub issues or pull requests.

| Test ID | Commit / environment | Result (Pass / Fail / Blocked) | Evidence reference | Defect / owner |
|---|---|---|---|---|
| AUTH-01 | | | | |
| AUTH-02 | | | | |
| DATA-01 | | | | |
| DATA-02 | | | | |
| LEARN-01 | | | | |
| CONTENT-01 | | | | |
| MOBILE-01 | | | | |
| PRIVACY-01 | | | | |

Release decision:

- [ ] All required technical checks passed.
- [ ] All critical defects are resolved and retested.
- [ ] Learner-protection and consent gates are complete for the intended cohort.
- [ ] The responsible adult operator has approved the cohort, test scope, and support process.
- [ ] The team understands that a small pilot provides usability and early learning evidence, not proof of broad or causal educational effectiveness.

**Decision:** Not approved / Approved for supervised pilot

**Responsible adult operator:**  
**Decision date:**  
**Conditions or exclusions:**
