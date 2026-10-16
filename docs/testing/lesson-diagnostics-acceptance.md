# Lesson Diagnostics — Acceptance Tests

**Status:** Acceptance test plan; not yet executed against live Streamlit/Auth0/Supabase.

| ID | Test | Expected result | Status |
|---|---|---|---|
| DG-01 | Validate the three current diagnostic schemas | Five distinct required stages, IDs, answers, and pathway question sets all validate | Not tested |
| DG-02 | Submit all correct answers | Score 5/5; Project placement | Not tested |
| DG-03 | Miss prerequisite item while getting all others right | Prerequisite review takes priority; prerequisite weakness is listed | Not tested |
| DG-04 | Score 2/5 with prerequisite correct | Level 1 — Easy | Not tested |
| DG-05 | Score 3/5 with prerequisite correct | Level 2 — Medium | Not tested |
| DG-06 | Score 4/5 with prerequisite correct | Level 3 — Hard | Not tested |
| DG-07 | Score 5/5 | Real-life project pathway | Not tested |
| DG-08 | Miss two tagged items | Both skill areas appear in the weakness report | Not tested |
| DG-09 | Submit with unanswered questions | No diagnostic result is saved | Not tested |
| DG-10 | Return to same lesson after diagnostic submission | Saved result is shown; there is no retake control | Not tested |
| DG-11 | Refresh or sign out/in after the diagnostic | Saved score, outcome, weaknesses, and route state restore | Not tested |
| DG-12 | Complete the lesson pathway | Post-lesson practice checkpoint is stored once | Not tested |
| DG-13 | Inspect normal course practice totals | Diagnostic questions do not inflate ordinary practice counts or accuracy | Not tested |
| DG-14 | Load an older progress JSON without diagnostics keys | Existing profile, progress, notes, and settings still load | Not tested |
| DG-15 | Use two separate test accounts | Each account sees only its own diagnostic data | Not tested |
| DG-16 | Test form, result and progress page on phone/tablet and desktop | No layout clipping, duplicate-key errors, or broken navigation | Not tested |
| DG-17 | Simulate a save failure after submission | Save failure is visible and the result is not falsely described as durably saved | Not tested |

## Test command
From the repository root, after installing project requirements:

```bash
python -m unittest discover -s tests -v
python -m py_compile data.py diagnostics.py logic.py state.py sections/course.py sections/progress.py
```

UI, persistence, account-isolation, refresh/re-login, and save-failure tests require a running preview deployment; these commands do not replace them.

## Recording each result
Record tested commit SHA, test date, environment/deployment, result, evidence link, defect ID, and retest result. Never mark a test “passed” solely because code compiles.


## Diagnostic unlock and repeatability checks

- [ ] Confirm the diagnostic is the first assessment for each of the three configured lessons.
- [ ] Confirm a saved diagnostic cannot be submitted a second time, including after refresh and re-login.
- [ ] Confirm prerequisite failure unlocks Level 1 only.
- [ ] Confirm score 1–2 with prerequisite correct unlocks Level 1 only.
- [ ] Confirm score 3 unlocks Levels 1–2.
- [ ] Confirm score 4 unlocks Levels 1–3.
- [ ] Confirm score 5 unlocks Levels 1–3 and the project.
- [ ] Confirm the learner can select any unlocked route before starting it.
- [ ] Confirm the selected route is persisted and cannot be changed by reopening the result screen.
- [ ] Confirm practice can be retaken with cleared answer-widget state and a separate attempt record.
- [ ] Confirm retakes do not modify or replace the original diagnostic result.
- [ ] Confirm diagnostic answers do not inflate ordinary practice question totals.
- [ ] Confirm the deployed app preserves diagnostic and route selection across refresh, logout, and login.

Do not mark the release validated until these integrated UI and persistence checks have been run against the deployed app.


## Lesson flow rebuild regression checks

- [ ] Open each configured lesson with no diagnostic record; diagnostic form is shown first.
- [ ] Submit diagnostic once; reopening the lesson shows the saved hub and does not offer a diagnostic retake.
- [ ] Select each unlocked route and confirm its own question set starts.
- [ ] Complete practice; exactly one attempt summary is stored and the completion screen renders without looping.
- [ ] Return to the hub; the same diagnostic remains and the completed attempt is listed.
- [ ] Start a second practice attempt; answer inputs are fresh and the second attempt is stored separately.
- [ ] Reopen a previously completed lesson; completion history does not block practice retakes.
- [ ] Refresh and sign out/in; diagnostic and attempt summaries restore from Supabase.
- [ ] Force a persistence failure and verify the UI clearly reports that the attempt may not be durable.
