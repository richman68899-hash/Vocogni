# Notes Folders — Acceptance Tests

Run on a preview deployment using test accounts and non-sensitive sample notes.

| ID | Test | Expected result | Result |
|---|---|---|---|
| NF-01 | Create folder with valid title | Folder card appears with selected color | Not tested |
| NF-02 | Create folder with blank title | Validation warning; no folder created | Not tested |
| NF-03 | Create duplicate folder title (case-insensitive) | Duplicate rejected | Not tested |
| NF-04 | Rename and recolor folder | New title and color remain after refresh | Not tested |
| NF-05 | Attempt nested folder creation | No nesting control exists | Not tested |
| NF-06 | Create note while viewing a folder | Note assigned to that folder | Not tested |
| NF-07 | Edit note title/content and folder | Changes save and remain after refresh | Not tested |
| NF-08 | Move note to another folder | Note appears in destination folder | Not tested |
| NF-09 | Move note to Unfiled | Note appears under Unfiled | Not tested |
| NF-10 | Delete folder containing notes | Folder removed; notes preserved as Unfiled | Not tested |
| NF-11 | Load pre-feature learner record | Existing notes remain visible as Unfiled | Not tested |
| NF-12 | Refresh and re-login | Folders and note assignments restore | Not tested |
| NF-13 | Sign in as a second test account | No first-account data appears | Not tested |
| NF-14 | Cause a controlled save failure in a safe test environment | UI does not claim changes were saved | Not tested |
| NF-15 | Test on mobile viewport | Controls remain usable; no clipping/key errors | Not tested |

Do not mark tests as passed until observed. Record build/commit, date, tester role (not personal details), result, and evidence reference.
