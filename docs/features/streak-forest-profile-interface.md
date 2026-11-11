# Streak Forest Profile interface

The Streak Forest is a focused sub-interface inside Profile → Learning Rhythm.

## Entry and layout
- The Profile page shows a compact Learning Rhythm summary and a **View streak forest** action.
- Forest artwork, tree slots, milestone cards, and management controls are hidden until the action is selected.
- **Back to Profile** returns to the normal Profile view without changing the app's main navigation route.

## Milestone mapping
- Each existing learner milestone can have at most one forest.
- A milestone without a forest is represented by a muted grey placeholder card.
- The learner can explicitly add a forest from that placeholder.
- Existing course-keyed forests from the first Streak Garden version are preserved in saved state but are no longer shown as separate forests.

## Streak evidence
A completed lesson checkpoint counts regardless of course, subject, or question result. A submitted answer with feedback, completed practice attempt, or completed diagnostic also counts. Activity is deduplicated by the learner's local calendar day, so multiple lessons on one day do not inflate the streak.

Simply opening the app or viewing an unfinished lesson does not count. Lesson completion timestamps come from the saved lesson-screen checkpoint. Older completed_lessons arrays contain lesson IDs without timestamps and cannot be backfilled into historical calendar dates reliably.

## Artwork
The interface uses four original local SVG assets in `assets/streak_forest/`: a landscape scene and three tree growth stages. The assets are embedded as data URIs at render time; no external image host is required. A text/emoji fallback remains if a local asset is missing.

## Persistence
The milestone-to-forest relationship is stored in the existing versioned `streak_garden` JSON object inside learner progress JSONB. The feature does not introduce a new table or modify Supabase schema.
