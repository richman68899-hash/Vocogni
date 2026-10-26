# Create Course — Feature Specification

**Status:** Proposed; specification only  
**Canonical parent:** [Phase 0 Master Implementation Structure](../phase-0-master-implementation-structure.md)  
**Priority:** High-value later-phase capability, gated by core learning and source contracts  
**Scope:** A safe authoring workflow for building a private, structured course in Vocogni

---

## 1. Product decision

Vocogni should have a dedicated **Create Course** experience because learner goals, school materials and subject coverage vary. The first version should create **private, editable course drafts**. It should not launch a public marketplace or permit generated questions to enter verified practice without review.

The promise is: turn a learning goal and relevant material into a structured course that the learner can inspect, edit, study and improve. Create Course must strengthen the learning loop—diagnose, understand, practise, apply, measure, update—rather than become a generic text-generation form.

## 2. Who can use it?

### Initial access model

- A signed-in learner can create and manage their own private drafts.
- A draft is visible only to its owner unless an explicit sharing model is later implemented.
- Publishing to a shared catalog is not part of the first version.
- Reviewer/educator permissions must be defined before shared publishing. Do not assume every signed-in account is a trusted reviewer.
- Do not add a dead navigation destination before the authoring flow is usable end to end.

## 3. User journey

1. **Define the goal.** Enter title, subject, level/grade band, learner goal, starting knowledge and intended outcome.
2. **Choose the basis.** Start from a blank course, selected existing Vocogni material or permitted learner-owned sources. Make source selection explicit.
3. **Create an outline.** Propose a small set of modules and lessons with learning objectives and prerequisite relationships.
4. **Review and edit.** Rename, reorder, add, remove and rewrite modules, lessons and objectives. AI suggestions must be visible and editable, never silently accepted.
5. **Add learning activities.** A lesson may include a concise explanation, worked example, practice, transfer/application task and a check for understanding. Offer only supported activity types.
6. **Validate.** Run deterministic structural checks for missing objectives, broken IDs, invalid ordering, missing scoring rules, invalid question definitions, prerequisites and source references.
7. **Preview as a learner.** Show the sequence as it will actually run, including empty, error and completion states.
8. **Save as draft.** Preserve edits on reload.
9. **Prepare for private study.** Show outstanding validation/review requirements. Questions not approved by VQE must not appear in verified-only banks.
10. **Revise or archive.** Editing after use creates a new draft/version. Existing attempts remain associated with the content version originally presented.

## 4. MVP scope

### Included

- An editable course outline with a bounded number of modules and lessons.
- Stable course, module, lesson and activity IDs.
- Objectives, prerequisites, activity order and expected outcomes.
- A structured lesson editor with preview.
- Validation feedback that points to the affected field or activity.
- Save, reopen, duplicate-as-new-draft, rename and archive.
- Source provenance for material imported or used to draft content.
- Explicit states: draft, needs_review, ready_for_private_study, published (reserved for later), and archived.
- A clear distinction between authored, AI-suggested, reviewed and verified material.
- Compatibility with existing question validation, skill taxonomy and durable-state behavior.

### Excluded from the first release

- Public sharing or a course marketplace.
- Payments, certificates, enrollment management or teacher analytics.
- Collaborative editing and version-merge tools.
- Unbounded file ingestion or large source payloads embedded in learner state.
- Automatic curriculum certification.
- A promise that AI can generate a complete, correct course in one click.
- Automatic promotion of generated questions to verified status.

## 5. Authoring model and contracts

A draft needs a stable ID independent of its title and a version that increments when learning content changes.

| Object | Required information |
|---|---|
| CourseDraft | course_id, owner_id, title, subject, grade/level band, goal, status, version, created/updated timestamps |
| Module | module_id, title, ordered lesson IDs |
| LessonDraft | lesson_id, module ID, title, objectives, prerequisites, ordered activity IDs, status |
| LearningObjective | stable ID, learner-facing objective, linked skill IDs where available, measurable success condition |
| ActivityDraft | stable ID, type, order, instructions, content, objective IDs, source references, review status |
| QuestionDraft | stable question ID, content version, response type, answer/rubric, grader contract, linked skill IDs, provenance, VQE status |
| SourceReference | source ID/version and resolvable location or excerpt reference; not just a decorative source title |
| ValidationReport | course/version ID, blocking errors, warnings, review requirements and last-run timestamp |

VQE remains the authority for question validation and verified-question selection. Reuse existing taxonomy IDs where they genuinely fit; do not invent skill IDs in the UI or use display labels as durable identifiers. Subjects without an established taxonomy need an explicitly provisional mapping until a governed taxonomy exists.

### Content status rules

- **Draft:** editable, not represented as reviewed or verified.
- **Needs review:** structural validation passed, but content or rubric review is still needed.
- **Ready for private study:** passed required structural checks; any assessment item in a verified-only path still needs separate VQE approval.
- **Published:** reserved for a later release with explicit reviewer permissions, provenance and release criteria.
- **Archived:** no longer offered as a new course; historical attempts remain readable.

Course-level readiness and question verification are separate concepts. A structurally valid course must not automatically make every question verified.

## 6. Validation rules

The first version should fail clearly and locally rather than produce an apparently complete but unusable course.

### Blocking errors

- Missing or duplicate stable IDs.
- A lesson references a nonexistent module or prerequisite.
- A prerequisite cycle or impossible sequence.
- A lesson has no learner-facing objective.
- An activity has an unsupported type or missing required fields.
- A question has an invalid answer format, missing expected answer/rubric or unusable grader.
- A question claims to assess a missing or invalid skill.
- A source-grounded activity refers to a missing, inaccessible or mismatched source version.
- An assessment route has no eligible questions and no explicit fallback.

### Warnings

- Objectives are vague or not observable.
- A course repeats content without explaining why.
- A lesson has no practice or transfer opportunity.
- A question's difficulty/skill mapping is provisional.
- A grade band or curriculum label has not been independently validated.
- Source extraction was incomplete.
- The course exceeds first-release size limits.

Warnings may be overridden only when the author decision is recorded and the override does not bypass security, structural correctness or VQE verification.

## 7. Relationship to Vocogni

- **Course catalog:** current authored courses live in data.py and course modules. Do not make user-authored drafts executable Python files or rewrite the catalog as part of the first builder.
- **Course runtime:** reuse the current lesson flow where the content contract is compatible. Identify unsupported activity types instead of silently ignoring them.
- **VQE:** reuse it for question structure, review snapshots, verification status, selection and attempt provenance. Never make a second verifier.
- **Skill taxonomy:** reuse stable IDs and prerequisites where applicable.
- **Diagnostics/grading:** keep scoring deterministic and subject-specific. AI may help draft a rubric but cannot become the scoring authority.
- **Progress/mastery receipt:** attempts must retain course, lesson, activity/question version, skill IDs and grading provenance so changed content does not overwrite history.
- **Persistence:** use the existing state dirty-mark and flush flow for durable mutations. No page-level direct Supabase writes.
- **AI adapter:** when available, AI may propose outlines, explanations, examples or question drafts through a validated service boundary. Manual authoring must still work if the model is unavailable.

### Storage decision gate

Phase 0 does not add a table or break the existing JSONB learner bundle. Before implementation, choose storage based on a bounded pilot:

- Keep large source files and extracted full documents out of the learner-state bundle.
- If a small private draft is stored in the current bundle for the pilot, set explicit size limits, preserve backward-compatible loading and test save/reload.
- If content, sharing, multiple authors or version history exceed the bundle's limits, design a separate storage migration with access controls, backup and rollback before shipping those capabilities.
- Do not describe an untested persistence path as complete.

## 8. UX requirements

Create Course should be a focused authoring flow, not a long chat transcript.

- Use grouped stages: **Goal → Outline → Lessons → Validate → Preview → Save**.
- Keep the course outline visible while editing a lesson where screen space permits.
- Provide one primary action per stage, clear back/continue controls and an unsaved-changes state.
- Show validation errors beside the affected item and in a concise summary.
- Use plain product copy; do not label generic generation as “personalized” without an observable input-to-output relationship.
- Make AI suggestions visibly editable and identify their sources.
- Match shared typography, colors, spacing, mobile layout, keyboard focus and reduced-motion behavior.
- Include a useful empty state and manual path; model credentials must not be required to create a blank course.

## 9. Acceptance criteria

### Functional

- An authenticated learner can create a private draft with a stable ID, edit it, save it, reopen it and archive it.
- Drafts are isolated by owner.
- Reordering or renaming lessons does not break stable IDs or historical attempts.
- Validation catches malformed structures and gives actionable messages.
- Preview matches the course that will actually run.
- A draft with no valid practice questions does not silently fall back to unverified questions.
- Source-based content retains source/version references.
- A model timeout or absent API key does not prevent manual course authoring.

### Learning quality

- Each lesson has an observable objective and an activity that can reasonably provide evidence for it.
- Question-to-skill mapping is reviewed where a stable taxonomy exists.
- Scoring rules are deterministic, versioned and tested.
- Generated question drafts remain out of verified-only selection until VQE approval.
- Reviewer checks distinguish source-supported facts from additions or assumptions.

### Persistence and security

- Save/reload is manually tested in the hosted signed-in app.
- One user cannot read or modify another user's private draft.
- Historical attempts remain linked to the original course/content versions.
- The UI reports save failure honestly and offers a recovery path.
- Private source content and credentials do not appear in logs.

### Evidence

- Unit tests cover contract validation, invalid references, duplicate IDs, dependency cycles, VQE integration and backwards compatibility.
- A manual checklist captures create → edit → reload → preview → validate → archive.
- A small learner-author usability test is recorded before broad release.
- Release notes distinguish automated checks, manual checks and unverified items.

## 10. Implementation sequence

1. **Contract first:** define draft schemas and pure validators; do not add the nav item yet.
2. **Manual builder:** create a blank course and edit its outline without a model dependency.
3. **Persistence spike:** test a bounded draft round-trip and decide whether the current bundle is sufficient.
4. **Preview/runtime bridge:** render a draft through supported course components without altering existing authored courses.
5. **VQE integration:** validate question drafts and keep unreviewed questions out of verified paths.
6. **AI-assisted drafting:** add outline/content suggestions behind the provider boundary after evaluation cases exist.
7. **Private pilot:** run the full hosted workflow and collect learner feedback.
8. **Shared publishing (later):** introduce reviewer permissions, release/version governance and any required storage migration only after the private pilot works.

## 11. Dependencies and release gate

**Dependencies:** reliable course/lesson/attempt flow; stable IDs and version contracts; source provenance where used; VQE integration; tested persistence and account isolation; shared UI tokens.

**Go/no-go decision:** implement the first Create Course UI only when the draft contract, save/reload design and verified-question behavior are testable. If those dependencies are not ready, keep authoring documented and continue using existing course modules without creating a misleading or half-functional navigation item.

## 12. Non-goals and product moat

A course builder alone is easy to copy and is not a defensible moat. The durable advantage should come from connecting learner-owned sources, structured objectives, verified questions, observable attempts, transparent skill evidence and appropriate next-step selection. Create Course should feed that loop instead of becoming another generic AI content generator.
