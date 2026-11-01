# Streak Garden v1 — implementation notes

## Product behavior

- Learning Rhythm replaces the former flame indicator with water imagery.
- Version 1 contains one Academic Garden. Each published Vocogni course receives an independent forest.
- One global water streak is calculated from existing meaningful learning events.
- Each forest uses seven-calendar-day cycles, anchored when that forest is created.
- Five distinct qualifying learning days plant a seedling; six grow a sapling; seven grow a mature tree.
- Trees remain in achievement history. Selling marks a tree sold, grants stage-based Dew, and frees an active slot.
- Forests have ten slots by default. The model accepts five or ten.
- When full, eligible milestones remain unclaimed. A later sale lets the next sync plant the oldest pending milestone.
- Dew is an append-only ledger. Water, planting, growth, and sale sources are idempotent.

## Source of truth

The existing Learning Rhythm activity evidence remains authoritative. A new grouped helper exposes the same saved practice, submitted-answer, and diagnostic dates per course. App opens and lesson views do not count.

Streak Garden does not create a second activity tracker or accept client-provided learning events. It consumes saved learner progress only.

## Persistence

The app stores learner profile, course progress, notes, and settings in the JSONB learner_progress.progress record. Streak Garden is an additive object in that record with schema_version 1.

No Supabase table migration is needed for v1. Old learner records safely receive an empty garden. Existing course progress and review history are unchanged.

## Modules

- enums.py: growth stages, tree status, and wallet reasons.
- models.py: typed domain models and JSON-state validation.
- rules.py: pure streak, cycle, growth, wallet, and resale calculations.
- engine.py: deterministic state transitions; no Streamlit or Supabase imports.
- ui.py: Streamlit rendering and explicit sell actions.
- learning_maintenance.py: adds grouped dates while retaining the global activity API.

## Verification

Run:

    python -m unittest discover -s tests -p 'test_streak_garden.py' -v
    python -m unittest discover -s tests -v
    python -m py_compile app.py learning_maintenance.py state.py sections/learning_rhythm.py streak_garden/*.py

Automated tests do not establish live Supabase write behavior, Streamlit visual behavior, or educational impact. Verify these separately before broad rollout.
