# Notes Folders — Feature Record

**Status:** Implemented on `feature/notes-folders`; validation pending  
**Proposed release classification:** Minor feature release (provisionally v1.3.0; do not tag until tested)

## Problem
As notes accumulate, a single flat list becomes harder to scan. Learners need a lightweight way to group notes without adding a nested folder hierarchy.

## Scope and behavior
- Create folders with a title and predefined color.
- Rename folders and change their color.
- Filter notes by all notes, Unfiled, or a specific folder.
- Create notes and assign them to a folder.
- Move notes between folders or back to Unfiled.
- Delete a folder without deleting its notes; affected notes become Unfiled.
- Folder nesting is not supported.
- Existing notes without a valid folder assignment remain available as Unfiled.

## Implementation
- `sections/notes.py`: folder cards, folder management, filtering, note assignment and movement.
- `state.py`: durable `note_folders` and `next_note_folder_id` state, serialization, and backward-compatible restore defaults.
- Persistence continues through `state.mark_persistent_dirty()` and the existing central autosave flow; no Supabase schema change is intended.

## Validation status
No claim of end-to-end correctness until the following are tested in the deployed preview:
- [ ] Python syntax/import check passes.
- [ ] Create, rename, recolor, and delete folder.
- [ ] Nested folders cannot be created.
- [ ] Create a note in a folder and edit its title/content.
- [ ] Move an existing note to another folder and to Unfiled.
- [ ] Deleting a folder preserves its notes as Unfiled.
- [ ] Existing accounts with notes but no folder fields still load.
- [ ] Folder and note assignments persist after refresh and re-login.
- [ ] Two accounts cannot see each other's folders or notes.
- [ ] Mobile layout is usable and no Streamlit widget-key errors occur.
- [ ] Autosave failure is visible and does not falsely report success.

## Evidence to retain
Add dated screenshots of folder cards, the editor's folder selector, and a move operation; record test results and known defects. Keep screenshots free of learner names, emails, tokens, and other personal data.

## Limitations / design decisions
- Colors are selected from a fixed palette rather than arbitrary color input.
- Folder records are flat by design.
- This change does not establish educational impact; it is an organizational usability feature.
- The code is in a feature branch and has not been merged or confirmed against live Auth0/Supabase services.
