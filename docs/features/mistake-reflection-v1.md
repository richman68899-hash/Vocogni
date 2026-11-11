# Mistake Reflection v1

## Purpose

Mistake Reflection collects the learner's own explanation of an incorrect answer. It is not an automated error diagnosis and does not affect scoring, marking, mistake counts, or question correctness.

## Experience

- After each incorrect answer, show an optional, collapsible reflection field.
- The learner may write a short explanation or continue without saving anything.
- The reflection is available for every question type and course because all lesson answers use the shared `sections/course.py` submission/feedback pipeline.
- When Settings uses deferred ("After submission") answer feedback, the reflection still appears after each incorrect answer. Full answer explanations remain deferred to the lesson summary.
- Saved reflections can be edited from the same answer feedback.

## Data contract

A course-progress record has an additive `mistake_reflections` list. Each record is linked to one answer by `answer_id` and includes:

- schema version;
- course, lesson, question, and attempt identifiers;
- learner-authored reflection text;
- source = `learner`;
- created/updated timestamps.

The original answer result retains its own correctness, marking, and provenance fields. Its `answer_id` links it to the reflection record. This keeps learner interpretation distinct from objective answer evidence and future AI-generated classifications.

## Persistence

Reflections are saved through the existing learner-progress JSONB record and autosave flow. Older learner records remain compatible: the collection is initialized when needed. No SQL migration or Notes changes are required.

## Future AI use

Future categorization can consume reflection records and propose patterns with evidence counts. Generated categories must remain distinguishable from learner-authored reflections and should not silently become facts about the learner.
