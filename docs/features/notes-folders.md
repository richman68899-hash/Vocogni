# Notes Folders — Feature Specification and Acceptance Record

**Status:** Implementation in progress  
**Target:** Vocogni prototype v1.3  
**Scope:** Notes and flat folders only

## User-facing behavior
- The index heading is **Folders**, not “Your folders”.
- Folder cards display a clean title and a pluralized count such as **0 Notes** or **1 Note**. No decorative parallelogram glyph is shown.
- A folder has an explicit **Open folder** action.
- Folder management is inside that folder's view.
- Folder contents are determined by each note's `folder_id`; folders cannot contain folders.
- In note cards, the destination control is labelled **Folders** and is positioned on the same row as the note title.
- The New note button is aligned with the Show selector in the folder index and the folder view.
- Palette: Red, Orange, Yellow, Green, Cyan, Blue, Pink, Purple, Grey, System.
- System uses a neutral foreground based on the selected appearance mode.
- Deleting a folder preserves its notes as Unfiled.

## Data compatibility
Folder records retain `id`, `name`, `color`, and `created_at`. Color may be stored as a semantic palette name; legacy hex values are mapped to the nearest supported semantic color during display/editing. Notes continue to use `folder_id`. No database schema change is required.

## Acceptance checklist
- [ ] Folder index title is “Folders”.
- [ ] No parallelogram glyph appears beside folder names.
- [ ] Open folder navigates to a folder-specific view.
- [ ] Folder management is only in the selected folder view.
- [ ] Notes created inside a folder are assigned to that folder.
- [ ] Existing notes remain available and invalid folder references become Unfiled.
- [ ] Rename/recolor survives refresh and re-login.
- [ ] All ten palette choices display correctly in light and dark appearance.
- [ ] Note destination control says “Folders” and sits beside note title.
- [ ] New note action aligns with the selector row.
- [ ] Folder deletion preserves notes as Unfiled.
- [ ] Two-account isolation remains intact.
- [ ] Mobile layout remains usable at narrow viewport widths.
- [ ] Syntax/import checks and integrated Streamlit/Auth0/Supabase tests pass.

Do not mark this feature complete until every applicable test has a recorded result and evidence link.
