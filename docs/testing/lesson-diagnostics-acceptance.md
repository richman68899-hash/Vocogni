# Lesson Diagnostics — Acceptance Tests

**Status:** Acceptance test plan; not yet executed against live Streamlit/Auth0/Supabase.

| ID | Test | Expected result | Status |
|---|---|---|---|
| DG-01 | Validate the three current diagnostic schemas | Five distinct required stages, IDs, answers, and pathway question sets all validate | Not tested |
| DG-02 | Submit all correct answers | Score 5/5; Project placement | Not tested |
| DG-03 | Miss prerequisite item while getting all others right | Prerequisite review takes priority; prerequisite weakness is listed | Not tested |
| DG-04 | Score 2/5 with prerequisite correct | Only Level 1 — Easy is unlocked | Not tested |
| DG-05 | Score 3/5 with prerequisite correct | Levels 1 and 2 are unlocked | Not tested |
| DG-06 | Score 4/5 with prerequisite correct | Levels 1, 2, and 3 are unlocked | Not tested |
| DG-07 | Score 5/5 | Levels 1–3 and the real-life project are unlocked | Not tested |
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
| DG-18 | Start a configured lesson with no saved diagnostic | Diagnostic appears first and is labelled Test 1 — Diagnostic | Not tested |
| DG-19 | Finish a practice test and choose Retake practice test | A fresh practice attempt starts; the diagnostic is not shown again | Not tested |
| DG-20 | Retake a practice test | Input widgets start blank and the prior attempt's answers are not reused | Not tested |
| DG-21 | Click Choose a practice test after diagnosis | A selector lists only the pathways unlocked by the diagnostic score | Not tested |
| DG-22 | Fail the prerequisite item with a high total | Only Level 1 is unlocked and prerequisite review is displayed | Not tested |

## Test command
From the repository root, after installing project requirements:

```bash
python -m unittest discover -s tests -v
python -m py_compile data.py diagnostics.py logic.py state.py sections/course.py sections/progress.py
```

UI, persistence, account-isolation, refresh/re-login, and save-failure tests require a running preview deployment; these commands do not replace them.

## Recording each result
Record tested commit SHA, test date, environment/deployment, result, evidence link, defect ID, and retest result. Never mark a test “passed” solely because code compiles.
