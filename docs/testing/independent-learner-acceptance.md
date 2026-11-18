# Independent Learner Acceptance Tests — Grade 7–9

**Purpose:** Verify that a learner can complete the supported learning journey without live coaching.
**Status:** Test plan; not executed.
**Safety:** Use synthetic accounts and data. Any learner research must be appropriately supervised and approved.

## Test protocol

- Recruit representative learners across Grades 7–9 and a range of prior attainment.
- Give each learner a device and task, not step-by-step instructions.
- Ask learners to think aloud only where that does not distort the task; record observed actions and confusion points with appropriate consent.
- Do not use real personal learning records in public issues or pull requests.
- Record build SHA, device/browser, viewport, network conditions, task outcome, time, help requests, recovery, and defect ID.
- Do not infer educational effectiveness from usability results.

## Critical tasks

| ID | Learner task | Pass condition | Failure signal |
|---|---|---|---|
| IL-01 | First visit: understand what Vocogni does | Learner can explain the purpose and identify the first action | Learner cannot distinguish course, diagnostic and practice |
| IL-02 | Choose a suitable course | Learner can identify a relevant course from title, topic, level and description | Learner chooses by guesswork or cannot tell whether content is appropriate |
| IL-03 | Start a lesson | Learner understands the objective and what success looks like | Learner starts answering without knowing the goal |
| IL-04 | Learn a new concept | Learner can explain the core idea in their own words after the explanation/example | Learner can only repeat wording or copy the example |
| IL-05 | Answer incorrectly | Learner understands what was wrong and what to try next | Feedback only says incorrect or reveals an unexplained answer |
| IL-06 | Get stuck | Learner can find a structured hint/help ladder without losing work | Learner guesses repeatedly, abandons, or depends on an AI answer dump |
| IL-07 | Retry after feedback | Learner receives a fresh but equivalent question testing the same skill | Same answer is memorised or question changes the target skill |
| IL-08 | Interpret a diagnostic | Learner understands that placement is provisional and not a grade or fixed ability label | Learner believes one short check proves mastery or inability |
| IL-09 | Interpret progress | Learner can distinguish completed work from demonstrated independent understanding | Percentage/streak is mistaken for mastery |
| IL-10 | Resume after leaving | Learner can identify what was saved and continue from the correct point | State silently disappears or save status is ambiguous |
| IL-11 | Recover from network failure | Learner sees an honest status and a safe retry path | UI implies a save succeeded when it did not |
| IL-12 | Find human help/report a problem | Learner can find a monitored support route and knows when to use it | No route exists, or route is unmonitored |
| IL-13 | Use on a phone | All essential content and controls remain readable and operable | Clipped math, hidden controls, tiny tap targets |
| IL-14 | Use with AI unavailable | Core learning, grading, feedback and recovery still work | AI provider failure blocks the learning journey |

## Required evidence fields

For each test, record:
- Test ID and scenario
- Build commit SHA and deployed version
- Synthetic learner label and grade band
- Device, browser, viewport and network
- Whether task completed without help
- Time to completion
- First point of confusion
- Number and type of recovery attempts
- Whether learner interpreted feedback correctly
- Defect severity, owner and retest result

## Release decision rules

- Any child-safety, privacy, data-loss, account-isolation or false-save defect is a release blocker.
- Any defect that prevents a learner from understanding feedback or continuing safely blocks the affected learning path.
- Do not average away a severe failure by counting successful tasks from other learners.
- Fix repeated confusion patterns before adding new engagement features.
- A usability pass does not prove learning gains, diagnostic validity, or mastery.
- Do not enable unsupervised public use until the legal, consent, safeguarding and monitored-support gates in `docs/testing/stage1-beta-acceptance.md` and `docs/legal/launch-readiness.md` are signed off by the responsible operator.
