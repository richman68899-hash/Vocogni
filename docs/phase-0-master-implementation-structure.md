# Vocogni — Phase 0 Master Implementation Structure

**Status:** Proposed implementation blueprint  
**Scope:** Product and technical foundation for the next learning-platform evolution  
**Repository baseline:** `main` at `0db4954ca5702240374840597a60da4af1eca57e` (26 October 2026)  
**Decision:** Phase 0 defines and tests the shared contracts. It does not attempt to ship every planned feature.

---

## 1. Executive intent

Vocogni should combine the strongest *learning patterns* demonstrated by leading education products without becoming a clone of any one product:

- **Source-grounded study workspace:** learners can bring class materials and receive explanations that point back to those materials.
- **Guided tutoring:** the system helps learners reason, asks useful questions, diagnoses misunderstandings, and avoids replacing the learner's thinking with an unexplained answer.
- **Structured course progression:** lessons, skill objectives, prerequisites, practice, checkpoints, and real-world application form a coherent sequence.
- **Evidence-based progress:** progress summaries show what the learner did, which skills the evidence supports, and what to practise next—without pretending that a few questions prove mastery.
- **A coherent learning loop:** diagnose → understand → practise → apply/transfer → measure → update the next step.

The differentiated product should be **a learning system that converts a learner's materials and observed work into a verifiable next learning step**, not a general-purpose chatbot with a course catalogue attached.

### Product outcome

For any supported course, Vocogni should eventually be able to answer five questions:

1. What is the learner trying to learn?
2. What evidence do we have about what they currently understand?
3. What is the smallest useful next learning activity?
4. Did the learner demonstrate the target skill on suitable evidence?
5. What should happen next—and why?

Phase 0 makes those answers consistent across the product.

---

## 2. Reference patterns and product decisions

These are patterns to learn from, not instructions to copy interfaces or proprietary content. Official product information reviewed on 25 October 2026 is linked in [Section 13](#13-reference-sources).

| Reference pattern | Useful learning mechanism | Vocogni decision |
|---|---|---|
| Gemini Notebook (formerly NotebookLM) | Source-grounded answers and citations; source-derived study materials; interactive learning overviews that combine summaries, slides/infographics, quizzes and flashcards; short video overviews; expanded quiz formats | Build a source-and-evidence layer first. Keep outputs grounded in selected sources, preserve provenance, distinguish drafts from approved content, and prioritize source-backed usefulness over media volume. Defer audio/video generation until core source accuracy and learner demand are demonstrated. |
| Khan Academy / Khanmigo | Skill-level progression, practice-linked feedback, prerequisite awareness, guided rather than answer-dumping tutoring | Keep learning objectives and question-to-skill links explicit. Tutor behavior should promote learner reasoning. Treat mastery as accumulated evidence, not a decorative percentage. |
| Gemini Guided Learning / Study Notebooks | Diagnostic baseline, bite-sized personalized lessons, follow-up checks, progress dashboard and visual explanations | Make the diagnosis-to-next-step loop coherent. Add generated lessons only after the course and evaluation contracts exist. |
| Coursera-style structured courses | Clear modules, sequenced instruction, graded/practice assessments and completion criteria | Make course structure, activity purpose, checkpoint rules and completion semantics explicit. Avoid implying certificates or accreditation that Vocogni does not provide. |

**Product principles derived from these patterns**

- A source is not automatically true or complete merely because it was uploaded.
- An AI explanation is not proof of learning; the learner must do something observable.
- Assessment results must be traceable to question versions, skills, scoring rules and attempts.
- A recommendation must state its reason and confidence/evidence limitation.
- Personalization should adapt the next activity, not arbitrarily change course content or scoring.
- Do not add flashy learning features before they improve understanding, practice quality, or the reliability of progress evidence.

---

## 3. Scope boundaries

### In scope for Phase 0

1. Define the product's learning loop, target users, primary use cases and non-goals.
2. Inventory existing systems and identify the single source of truth for each responsibility.
3. Define shared domain objects and interface contracts.
4. Define how course content, imported sources, questions, learner attempts and skill evidence relate.
5. Specify the boundaries for tutoring/AI services, source citations, validation and fallback behavior.
6. Specify navigation, page hierarchy and the shared visual design system.
7. Define privacy, data minimization, failure recovery and observability requirements.
8. Establish automated quality gates and a release-evidence checklist.
9. Build a feature-to-phase roadmap with measurable acceptance criteria.

### Out of scope for Phase 0

- Rewriting Streamlit, Auth0, Supabase, or durable learner-state persistence.
- A database migration or normalized multi-table redesign.
- Shipping a fully autonomous course generator.
- Treating LLM-generated questions as verified without review.
- Adding every media format, podcast, flashcard, mind map, collaboration, teacher dashboard or mobile feature immediately.
- Claiming validated mastery, causal learning gains, official curriculum alignment, or accreditation without supporting evidence.
- Optimizing for feature count, animated dashboards, or vanity engagement metrics.

**Rule:** Phase 0 may create documentation, contracts, schemas, tests, and small compatibility helpers. Any learner-visible feature that needs a new data flow should be specified here and implemented in its own later phase.

---

## 4. Existing architecture: retain and clarify

The current architecture should remain the baseline until measured evidence justifies a change.

| Responsibility | Existing home | Phase 0 rule |
|---|---|---|
| App startup, authenticated session, navigation and top-level routing | `app.py` | Keep this file an entry point, not a place for learning logic. |
| Learner session state and durable save coordination | `state.py` | Preserve existing dirty-state and flush semantics. |
| Database operations | `persistence.py` | Keep Auth0 identity separate from Supabase Auth; do not introduce a second competing save path. |
| Current durable learner bundle | Supabase PostgreSQL JSONB through `persistence.py` | Preserve backward compatibility. Do not migrate the schema during Phase 0. |
| Course and authored learning content | `data.py`, course modules and `sections/course.py` | Keep content distinct from rendering; introduce contracts before expanding content ingestion. |
| Rule-based progress, recommendations and mastery receipt | `logic.py` and related modules | Keep deterministic logic testable without a Streamlit runtime. |
| Diagnostic schema and scoring | `diagnostics.py`, grading modules | Scoring rules must be explicit and testable. |
| Verified authored-question catalogue and review status | `question_engine.py` | Reuse VQE. Do not create a competing question bank or verified-status system. |
| Stable math skill IDs and prerequisite metadata | `math_taxonomy.py` | Reuse stable IDs; do not identify a skill by display text alone. |
| Main learner experiences | `sections/*.py` | Keep UI composition separate from decisions, scoring, persistence, and provider calls. |
| Shared visual system | `styles.py`, `.streamlit/config.toml` | Establish tokens and reusable patterns instead of adding one-off CSS in every page. |

### Required architecture constraints

- Auth0 remains the identity provider; Supabase remains the durable data store.
- No secrets, model API keys, or private learner content in source control or logs.
- Existing learner records must continue to load even when optional new fields are absent.
- Pure domain functions should accept plain data and return plain data; avoid importing Streamlit into the learning engines.
- VQE remains the source of truth for question verification and strict verified-only retrieval in pilot lessons.
- UI copy must distinguish prototype heuristics from externally validated assessment.
- If the hosted app or signed-in save/reload path has not been tested for a release, report that gap explicitly.

---


### 4.1 Repository-level implementation structure

**Keep the current file layout stable during Phase 0.** The existing codebase already has clear responsibility boundaries; a large folder migration would add risk without improving the learning journey. This is the working ownership map for the next increments.

```text
Vocogni/
├── app.py                         # startup, authentication, navigation, top-level lifecycle
├── state.py                       # session state + durable-save coordination
├── persistence.py                 # Supabase persistence boundary
├── logic.py                       # deterministic recommendations, evidence summaries, mastery receipt
├── question_engine.py             # the single question validation/review/selection authority (VQE)
├── math_taxonomy.py               # stable math skill IDs and prerequisite metadata
├── diagnostics.py                 # diagnostic contracts, scoring and routing checks
├── *_grading.py                   # subject-specific scoring rules
├── data.py + *_course.py          # authored course/lesson content
├── revision_sprint.py             # shared revision-session orchestration
├── sections/
│   ├── browse.py                  # course library + entry into a course
│   ├── course.py                  # lesson/diagnostic/practice learner flow
│   ├── progress.py                # progress and evidence presentation
│   ├── notes.py                   # learner notes and milestones
│   ├── profile.py                 # profile
│   └── settings.py                # learner-controlled display/learning preferences
├── styles.py + .streamlit/        # shared visual system and base theme
├── components/                    # focused reusable front-end components (currently whiteboard)
├── tests/                         # deterministic tests and compatibility/integration checks
└── docs/
    ├── phase-0-master-implementation-structure.md  # canonical blueprint
    ├── features/                  # bounded feature specifications
    └── testing/                   # acceptance and manual verification checklists
```

Treat this as an ownership map, not a mandate to move files. New modules should be added only when a real feature needs a separately testable boundary.

#### Proposed future modules (do not create them just to match this diagram)

Only when the corresponding phase begins and its acceptance tests are defined, consider:

- `source_records.py` or a small `sources/` package for source metadata, versions, access control and extraction status.
- `ai_provider.py` or `services/ai_provider.py` for one provider-neutral model boundary, schema validation, timeout handling and deterministic fallback.
- `next_step_policy.py` for a pure, testable next-activity policy if that policy becomes more complex than the current `logic.py` responsibilities.
- A separate retrieval/index module only when an actual source-grounded feature is ready to be implemented and its privacy boundary is specified.

Do not move existing files into new packages as a cleanup exercise. If a module is moved later, keep the PR narrowly scoped and run import, unit, persistence-compatibility and hosted smoke tests.

#### Phase 0 artifact map

Phase 0 should produce a small, reviewable set of artifacts rather than a large documentation tree:

| Artifact | Canonical location | Purpose |
|---|---|---|
| Master plan, boundaries, phases, cross-cutting contracts | `docs/phase-0-master-implementation-structure.md` | Single source of truth for what is proposed and why |
| Feature-specific behavior and acceptance requirements | `docs/features/<feature>.md` | Contract for one bounded implementation |
| Manual and end-to-end verification | `docs/testing/<flow>-acceptance.md` | Reproducible UI, persistence and failure checks |
| Automated checks | `tests/` and `.github/workflows/` | Catch regressions without requiring the hosted UI |
| Architecture decisions | Add short ADR files only as decisions actually need durable records | Capture context, decision, trade-offs and revisit trigger; avoid speculative ADR bureaucracy |

**Definition of a code change:** a feature PR must cite the relevant contract and state its scope, tests, manual checks, persistence/security impact, limitations and rollback/disable path. The master blueprint itself is not a substitute for implementation or live verification.

---

## 5. Target architecture and ownership boundaries

This is a **logical architecture**. The named future modules are proposals, not instructions to create every file in Phase 0.

```text
Vocogni application
│
├── Experience layer
│   ├── app.py + sections/*
│   ├── course / source workspace / tutor / progress / notes
│   └── styles.py (shared UI tokens and patterns)
│
├── Learning orchestration layer  [define contract in Phase 0]
│   ├── choose next activity from explicit evidence
│   ├── select appropriate verified practice
│   └── prepare a learning plan / mastery receipt
│
├── Domain engines (mostly existing)
│   ├── question_engine.py + math_taxonomy.py
│   ├── diagnostics.py + math_grading.py / chemistry_grading.py
│   └── logic.py + learning_maintenance.py + revision_sprint.py
│
├── Content and evidence layer  [contract first; implement incrementally]
│   ├── authored course content
│   ├── imported source records + source excerpts/citations
│   └── generated draft materials with provenance and review state
│
├── AI/provider boundary  [future; not required to complete Phase 0]
│   ├── one provider-neutral interface
│   ├── source-grounded retrieval and response checks
│   └── safe deterministic fallback when unavailable
│
└── Persistence and observability
    ├── state.py → persistence.py → Supabase JSONB
    ├── versioned learner activity/evidence records
    └── privacy-safe error diagnostics and evaluation logs
```

### Ownership rule

Each concept must have one authoritative owner. For example, question validity belongs to VQE; skill identity belongs to the taxonomy; score calculation belongs to the relevant grader; learner-state persistence belongs to the existing state/persistence path. Other components can consume these outputs but should not silently recalculate them with different rules.

---

## 6. Shared domain contracts

Phase 0 should document and validate contracts before adding new integrations. Avoid building a general-purpose framework for hypothetical future use cases.

### 6.1 Core objects

| Object | Minimum conceptual fields | Notes |
|---|---|---|
| `Course` | stable `course_id`, title, level/grade band, subject, ordered lesson IDs, status | Course IDs must survive title edits. |
| `Lesson` | stable `lesson_id`, course ID, learning objectives, prerequisites, explanation, activities, checkpoint rules | Each lesson describes what the learner should be able to do. |
| `Skill` | stable `skill_id`, label, strand, objectives, prerequisites, common misconceptions | Use taxonomy IDs; labels may evolve. |
| `Question` | stable question ID, version, prompt, response type, grader contract, answer/rubric, skill IDs, purpose, difficulty, verification status | Reuse the VQE record and status conventions. Store version/provenance with attempts. |
| `SourceArtifact` | stable source ID, owner, source type, title, content hash/version, ingestion status, created time, access policy | Phase 0 defines requirements; later work selects file storage and ingestion mechanics. |
| `EvidenceSpan` | source ID/version, excerpt or locator, page/section/timecode, content hash | A citation must resolve to the relevant source location, not just a source title. |
| `LearningPlan` | goal, source/curriculum context, target skills, baseline evidence, ordered activity IDs, status, plan version | Plans should be inspectable and revisable by the learner. |
| `DiagnosticRecord` | diagnostic ID/version, question IDs/versions, answers, scoring-rule version, outcome, limitations | A baseline is an initial signal, not a definitive skill label. |
| `AttemptRecord` | attempt ID, question ID/version, learner response, score, grader/version, timestamps, skill IDs, verification provenance | Preserve old results if content changes. |
| `SkillEvidence` | skill ID, evidence source, result, context, recency, uncertainty/limitations | A percentage alone is not sufficient mastery evidence. |
| `Recommendation` | action, reason, supporting evidence, target skill/activity, expiry or freshness | Learners should understand why an action is recommended. |
| `MasteryReceipt` | skill IDs, evidence summarized, strengths/gaps, evidence limitations, recommended next action | A transparent evidence summary, not a certificate. |

### 6.2 Cross-cutting contract requirements

- Stable IDs are machine-facing; labels and UI copy are presentation-facing.
- Every versioned object must tolerate missing optional fields during backward-compatible reads.
- Dates use one explicit timezone convention and ISO-8601 serialization.
- Generated material must distinguish `draft`, `review_needed`, `approved`, and `retired` states; generated does not equal approved.
- Learner-visible percentages must state what was counted and over which attempts.
- Persisted records should be compact, bounded and serializable; do not store full prompts or entire uploaded documents repeatedly inside every attempt.
- Define a record-version and migration strategy before changing durable shapes. Phase 0 itself must not introduce a breaking state migration.

### 6.3 Question-to-skill contract

The first implemented shared-record slice is the [Question-attempt provenance contract](features/question-attempt-provenance.md). It versions new question provenance metadata while leaving historical learner records untouched; this is a narrow implementation of the broader domain-contract work, not completion of P0.3.

A question should be linked to the skill it actually assesses, not merely the broad lesson topic. The VQE metadata is authoritative for reviewed questions. For legacy history, preserve compatibility and label evidence quality honestly. If a question is retired, changed, or its review snapshot becomes stale, previous attempts remain historical evidence but must not be silently treated as an attempt on the new version.

---

## 7. Source-grounded learning contract

This is the foundation for the strongest NotebookLM/Gemini Notebook-inspired workflow.

### Source lifecycle

```text
Add source
  → validate type/size/access
  → extract text and structural locations
  → record source ID + version/hash
  → mark extraction quality and limitations
  → make searchable within the learner's permitted workspace
  → generate an answer or draft learning resource
  → attach source evidence to supported claims
  → run quality checks
  → show output with citations and uncertainty
```

### Requirements

1. **Scope:** source-grounded answers use the learner's selected source set unless the UI explicitly states that external knowledge is being used.
2. **Citations:** factual claims about uploaded course material should point to a page, heading, paragraph, question, or timestamp where technically available.
3. **Evidence coverage:** the system must be able to say that it could not find a supporting passage. It must not fabricate a page number or citation.
4. **Conflicts:** when two sources disagree, show the conflict and identify the sources rather than silently reconciling them.
5. **Extraction quality:** scanned, incomplete, corrupted, or poorly structured sources need a visible quality warning.
6. **Versioning:** if a source changes, previously generated materials retain the source version they used.
7. **Draft status:** generated notes, lessons, flashcards and questions start as drafts. Question drafts enter VQE review before they can be served as verified questions.
8. **Isolation:** one learner must not retrieve another learner's private sources or derived materials.
9. **Fallback:** when retrieval or the model is unavailable, explain the limitation and preserve access to authored course content.
10. **No false completeness:** summarizing a file does not prove every detail was extracted or included.

Phase 0 defines the source contract and test cases. It does not need to ship ingestion or generation.

---

## 8. Tutor and adaptive-learning contract

### Tutor interaction pattern

```text
Learner goal / question
  → determine task type and known context
  → identify relevant skill and source/content evidence
  → ask a clarifying question only when needed
  → choose: explain, demonstrate, hint, question, feedback, or transfer task
  → check understanding with learner work
  → record the observable evidence
  → propose the next action with a reason
```

### Tutor behavior requirements

- Do not reveal a final answer by default when a guided prompt or hint can move the learner forward; make direct worked solutions available when the learning goal requires them.
- Prefer one useful question at a time over a long generic Socratic interrogation.
- Give a hint ladder: orienting cue → relevant principle → partial setup → worked example/solution when appropriate.
- Use the learner's actual answer and the question's verified rubric/grader. Do not create score rules inside the model prompt.
- Clearly separate source facts, deterministic grading, and AI-generated interpretation.
- Explain uncertainty and request clarification when the source or problem statement is ambiguous.
- Any AI-generated visual, analogy, or extra example must not alter the underlying mathematical/scientific truth or imply that a draft has been verified.
- Do not infer a stable learner trait from one error. Record task-level evidence and update the plan cautiously.
- Follow age-appropriate interaction, privacy, and educational-safety requirements.

### Adaptive next-step rules

The next activity can be selected from a small, inspectable set:

1. prerequisite review,
2. concept explanation,
3. worked example,
4. verified targeted practice,
5. transfer/application task,
6. spaced review,
7. retest/checkpoint,
8. learner-chosen exploration.

Selection should consider target skill, prerequisite status, verified-question availability, recency of evidence, task difficulty, and learner preference. A recommendation must have a readable reason. If evidence is insufficient, choose a reasonable baseline activity and state why rather than fabricating personalization.

**Important:** In Phase 0, define the interface and decision policy. Reuse the current VQE, taxonomy, diagnostic and progress logic. Do not build a second adaptive engine alongside them.

---

## 9. Product information architecture and visual system

The product should present one connected journey rather than a collection of unrelated AI tools.

### Proposed primary navigation

- **Home:** resume the most relevant activity and see one next-step recommendation with its reason.
- **Learn:** course library, course map, lessons, diagnostics and practice.
- **Study materials:** learner-owned sources, notes and source-grounded study resources.
- **Tutor:** guided help tied to the current course, skill, or selected source.
- **Create Course** (private-draft route): create and revise owner-only course drafts. Keep it hidden until the manual authoring, validation and save/reload path is functional; shared publishing requires explicit reviewer permissions.
- **Progress:** evidence by skill, course completion, recent attempts, review schedule and the next recommended action.
- **Settings / Profile:** learner preferences, identity, privacy and account controls.

This navigation is a target. Do not add empty destinations just to match the proposed map. Phase 0 must map each route to existing views, define missing views, and select a sequence for implementing them.

### Visual system requirements

- One primary type family with a deliberate type scale; use a distinct monospace face only where numeric or technical formatting benefits.
- A restrained palette with high-contrast text, one primary action color, neutral surfaces, and semantic colors reserved for real states.
- A consistent spacing/radius/border scale; avoid one-off gradients, heavy shadows, emoji as structural icons, and redundant cards.
- Consistent page titles, brief page introductions, section headings, empty states, loading states, errors and save status.
- Responsive layouts that work on mobile-sized screens as well as desktop.
- Visible keyboard focus, reduced-motion support, readable line length, and functioning learner-controlled text size/theme preferences.
- No decorative metric unless it changes a decision. Progress charts must have clear definitions and honest limitations.
- Use plain, specific product copy. Avoid generic AI claims like “revolutionary,” unexplained score labels, and claims of mastery that the evidence cannot support.

Phase 0 should create a page-by-page audit and shared design tokens in `styles.py`; it should not rewrite all pages in one risky patch.

---


### Create Course — course-authoring experience

**Decision: applicable, but ship it in stages.** Vocogni needs a controlled way to create personal courses because learner goals, school materials and subject coverage vary. The first release should create **private, editable drafts**; a public catalog, shared publishing and a fully autonomous course generator are later capabilities.

The authoring journey is: **Goal → Outline → Lessons → Validate → Preview → Save**.

- **Goal:** title, subject, level/grade band, learner goal, intended outcome and any selected source material.
- **Outline:** an editable sequence of modules, lessons, observable objectives and prerequisites.
- **Lessons:** concise explanations, worked examples, supported practice, transfer/application tasks and checks for understanding. AI suggestions are drafts that the author can edit or reject.
- **Validate:** deterministic checks for stable IDs, objective coverage, references, question/grader structure, prerequisites, activity types and source provenance.
- **Preview:** show the actual learner-facing sequence before it is saved for use.
- **Save and revise:** keep a private draft, reopen it, and preserve content versions so historic attempts do not silently point at changed questions.

**Important authority boundaries**

- The course builder does not replace VQE. Generated questions stay unverified until they pass the existing review process.
- It does not create a competing skill taxonomy, scoring engine or direct Supabase write path.
- Use the current learner-state dirty/flush flow; decide storage limits before persisting large draft bodies. No database migration is part of Phase 0.
- Distinguish course structural readiness from question verification and from validated learning outcomes.
- A learner can create a blank course manually without an AI API key. AI-assisted drafting is an optional accelerator, not a dependency.

**Access and release model**

Start with owner-only private drafts. Do not expose a universal Create Course route until the basic flow works end to end. Shared publishing requires a separate permission model, review workflow, versioning, archive/rollback behavior and account-isolation tests.

**Phase placement:** define the contracts in Phase 0; pilot a small private Create Course workflow after source provenance, core lesson flow and bounded persistence are reliable; keep reusable authoring, educator review and shared publishing in the wider authoring phase.

Detailed flow, data contract, validation rules, UX requirements and acceptance tests: [Create Course feature specification](features/create-course.md).

## 10. Persistence, security and privacy

### Persistence boundary

The current durable learner-state flow remains authoritative:

`section interaction → state.mark_persistent_dirty() → state.flush_persistent_save() → persistence.py → Supabase JSONB`

Phase 0 must document:
- which fields are transient UI state versus durable learner data;
- what constitutes a meaningful state mutation;
- which failures must block a logout or navigation action;
- how old records load when new optional fields are absent;
- how save status is displayed and verified; and
- how a new data shape would be introduced without losing a learner's existing progress.

Do not add direct Supabase writes from individual pages. Avoid saving every UI rerun or persisting data that is not useful for learning or product reliability.

### Security/privacy requirements

- Validate the authenticated user on every read/write path; never trust a client-provided user ID alone.
- Verify account isolation with tests.
- Store only information needed to deliver the learning experience and evaluate it.
- Do not log raw private notes, source contents, access tokens, credentials, or full model prompts containing learner data.
- Keep uploaded-source access control and retention/deletion behavior explicit.
- Handle provider timeouts, rate limits, malformed outputs and unavailable credentials without crashing the core course experience.
- Document which AI provider receives which learner/source data before enabling a real provider.
- Make user-facing claims about privacy match actual storage, retention, provider and model-training practices.

These are release requirements, not reasons to over-engineer the prototype before the contracts are clear.

---

## 11. Evaluation and acceptance framework

A product feature is not complete because it renders or because a demo looks convincing. Each capability needs four kinds of evidence.

### A. Functional correctness

- input validation and expected outputs;
- malformed input and missing optional-field handling;
- scoring and VQE validation;
- no source/learner-state mutation by read-only selectors;
- correct next-step routing and attempt metadata;
- save/reload behavior and account isolation.

### B. Learning quality

- a teacher or qualified reviewer checks authored content and rubrics;
- tutor hints advance reasoning rather than leak answers unnecessarily;
- generated claims and citations can be checked against sources;
- questions actually target their assigned skills;
- recommended next actions follow documented policy;
- learners can complete the activity without being trapped by an invalid or unavailable question.

### C. Usability and accessibility

- a first-time learner can identify where to start;
- the principal action on each screen is clear;
- a learner can understand why an activity is recommended;
- empty/loading/error/success states are present;
- keyboard focus, readable text and mobile layouts are checked;
- no interface claims an action saved unless the save path confirms it.

### D. Real-user evidence

- define a test question or learning outcome before testing;
- observe representative learners completing a defined task;
- record confusion, completion, incorrect responses, help needed and failure cases;
- ask for user feedback without leading questions;
- preserve anonymized notes and an explicit limitation statement;
- do not equate satisfaction, time-on-page, or repeated clicks with learning gain.

### Required feature release packet

Each implementation PR should state:
1. user problem and target outcome;
2. files/interfaces changed;
3. acceptance criteria;
4. automated tests and results;
5. manual UI paths checked;
6. persistence/security impact;
7. known limitations;
8. rollback or disable path;
9. screenshots or short demo where UI change merits it;
10. what remains unverified.

---

## 12. Phase 0 work packages, sequence and completion gates

Phase 0 is complete only when the following work products exist and are reviewed. The sequence is intentional: establish intent and ownership before interfaces, then define tests before building new features.

| ID | Work package | Deliverable | Completion gate |
|---|---|---|---|
| P0.1 | Product doctrine and reference map | Product principles, target learner problems, non-goals, feature-to-reference map | Each proposed feature serves a named learning problem and has a measurable outcome. |
| P0.2 | Existing-system inventory | Module ownership map, flow diagrams, architecture decision records | Every core responsibility has one owner; no duplicate learning/scoring/persistence engines are proposed. |
| P0.3 | Domain contracts | Object definitions, stable-ID/version rules, serialization examples | Existing objects are mapped; backward compatibility and version behavior are documented. |
| P0.4 | Learning-policy contract | Tutor behavior, next-step options, evidence/misconception rules | Policy is testable and can fall back without a model. |
| P0.5 | Source/evidence contract | Source lifecycle, citations, ingestion-quality states, privacy boundary | Every generated claim intended to be grounded has a testable citation and failure behavior. |
| P0.6 | AI boundary and evaluation plan | Provider-neutral interface proposal, output schema, failure policy, eval dataset spec | No feature silently depends on one vendor; malformed or unsupported outputs fail safely. |
| P0.7 | Navigation and visual system spec | Route map, page purpose, design-token and component rules | Each page has one primary job/action; design tokens are centralized. |
| P0.8 | Persistence and privacy review | Durable/transient state inventory, account-isolation checklist, migration policy | No schema migration needed for the blueprint; future state changes require a compatibility plan. |
| P0.9 | Quality/release gates | Test matrix, manual smoke-test checklist, PR/release packet template | CI and manual acceptance criteria are explicit; hosted behavior is never implied by unit tests. |
| P0.10 | Prioritized implementation backlog | Phase 1+ feature cards with dependencies, value, risk, owner and acceptance criteria | The first implementation phase is small enough to validate end-to-end before broad expansion. |

### Suggested sequence

**P0-A — Audit:** P0.1, P0.2  
**P0-B — Contracts:** P0.3, P0.4, P0.5, P0.6  
**P0-C — Experience and operations:** P0.7, P0.8, P0.9  
**P0-D — Prioritize and sign off:** P0.10

Do not parallelize conflicting edits to shared architecture documents. Every decision should say whether it is a current fact, a proposed target, or an unverified assumption.

---

## 13. What follows Phase 0

This is a proposed sequence, not a promise that every feature will be built. Each phase should stop or change direction if its learning/user evidence is weak.

### Phase 1 — Reliable core learning journey
- Audit and repair the current learner journey.
- Make the current course → lesson → attempt → feedback → progress path consistent.
- Confirm question versions, skill IDs, scoring and save status stay connected end to end.
- Conduct hosted signed-in save/reload and account-isolation tests.

**Exit criterion:** a real learner can finish a supported lesson, see a truthful result, reload the app, and find their durable progress intact.

### Phase 2 — Source-grounded study workspace
- Add sources and source records with permission checks and source versions.
- Extract and display usable passages with document locations.
- Add retrieval and citation checks before source-grounded answers.
- Start with concise summaries and “ask this source” interactions; keep unsupported claims visible.

**Exit criterion:** tested answers cite the right source locations, unsupported answers are flagged, and learner data remains isolated.

### Phase 3 — Guided tutor, connected to course context
- Tutor mode for hints, guided questions, explanation and worked examples.
- Use current skill/question context and approved course/source evidence.
- Log the tutoring task type and learner response as evidence where appropriate—not every private utterance by default.
- Add safe fallback for missing provider credentials, failure and poor outputs.

**Exit criterion:** the tutor helps learners complete defined tasks; output quality is reviewed and failure handling works.

### Phase 4 — Evidence-driven adaptation
- Integrate the current VQE and skill taxonomy with the next-step policy.
- Use prerequisite review, targeted practice, application and spaced review.
- Explain recommendation rationale and show the underlying evidence and its limitations.
- Evaluate whether the selected next activity fits the learner's demonstrated needs.

**Exit criterion:** recommendations are reproducible from the documented policy and traceable evidence.

### Phase 5 — Study-material generation and a private Create Course pilot
- Generate draft flashcards, quizzes, study guides and lesson summaries from approved sources/course material.
- Link each item to its source and target skill.
- Pilot a bounded private course-draft workflow: editable outline, objectives, lesson order, validation, preview and save/reload.
- Require review for generated questions before verified use; keep course readiness separate from question verification.
- Measure source/assessment error rates, author effort and learner usefulness before expanding scope.

**Exit criterion:** generated study materials meet predefined accuracy/provenance thresholds, a small private course can be created and reopened reliably, and no unreviewed questions enter the verified bank.

### Phase 6 — Transfer, retention and visual explanation
- Interactive diagrams/visual explanations where a visual improves understanding.
- Application projects and delayed retrieval checks.
- Optional audio overview or alternate-format study materials when learner testing demonstrates demand.
- Retention evidence over time rather than single-session scores.

**Exit criterion:** a small set of visual/transfer/retention activities demonstrates utility in user testing.

### Phase 7 — Shared course publishing and authoring at scale
- Expand beyond the private Create Course pilot into reusable authoring and release workflows.
- Add explicit reviewer/educator permissions, review queues, course versioning, release notes, archive/rollback and content-quality reporting.
- Add subjects only when the taxonomy, question contracts, rubrics and review process can support them.
- Consider more durable normalized event/data architecture only when measured scale or analysis needs justify migration; include backup and rollback planning.

**Exit criterion:** a new course can be authored, validated, reviewed, released, revised and monitored without changing shared engine code for each course; access controls and historical attempt versions remain correct.

---

## 14. First build backlog: convert this blueprint into small PRs

The recommended immediate post-Phase-0 order is:

1. **Architecture contract docs:** add/maintain the module ownership map, object contracts, decision records and feature matrix.
2. **VQE contract hardening:** document the verified-question authoring/review lifecycle and ensure every new learner-facing attempt retains question version and skill evidence.
3. **End-to-end test harness:** test diagnostic → lesson route → verified practice → result → mastery receipt → durable save/reload.
4. **Page/visual audit:** map every page to one purpose and one primary action; consolidate styling in the shared design system.
5. **Create Course contract and storage spike:** use the feature spec to validate the private-draft model, stable IDs, VQE rules and save/reload limits before building the UI.
6. **Source-workspace spike:** test one source type, one source citation format and one learner task before implementing a generic ingestion pipeline.
7. **AI adapter spike:** only after the source contract and test set exist; keep provider-specific behavior behind one interface and retain deterministic fallback.

Each backlog item should be delivered as a bounded PR with tests and evidence. Do not stack all seven into one enormous merge.

---

## 15. Decisions to record before implementation

Create short Architecture Decision Records (ADRs), each with context, options, decision, trade-offs, consequences and revisit trigger:

- **ADR-001 — Durable learner state:** retain the current Supabase JSONB bundle during the next feature increments; no migration without measured need and an explicit rollback plan.
- **ADR-002 — Verified question authority:** VQE is the only question verification/retrieval authority for its supported scope.
- **ADR-003 — Stable skills:** stable taxonomy IDs, never display labels as the durable identity of a skill.
- **ADR-004 — AI boundary:** no UI module calls a model provider directly; centralize provider calls and enforce schemas/evaluation/fallback.
- **ADR-005 — Source citations:** source-grounded claims must carry resolvable provenance; no fabricated citations.
- **ADR-006 — Mastery semantics:** distinguish activity/completion, observed performance, provisional skill evidence and validated mastery.
- **ADR-007 — Generated content state:** generated materials are drafts until validated; VQE review is required before a question is served as verified.
- **ADR-008 — Release evidence:** unit tests, UI-path tests and hosted persistence smoke tests are distinct evidence and reported separately.

These are recommended decisions for review, not proof that all ADRs have already been implemented.

---

## 16. Definition of done for Phase 0

Phase 0 is ready to sign off when:

- [ ] Product principles, target problems and explicit non-goals are recorded.
- [ ] Existing modules and authoritative responsibilities are mapped.
- [ ] The target architecture has no duplicate question, skill, grading or persistence engine.
- [ ] Domain contracts include IDs, versions, provenance, uncertainty and backward compatibility.
- [ ] Source-grounded answer requirements define citations and failure behavior.
- [ ] Tutor and next-step policies can be tested without an LLM.
- [ ] The target navigation and shared visual system are documented.
- [ ] Security, account isolation, privacy and persistence requirements are listed.
- [ ] Every proposed later-phase feature has a user outcome, dependencies and acceptance criteria.
- [ ] Create Course has an explicit private-draft scope, VQE boundary, version/provenance rules, storage decision gate and release criteria.
- [ ] A bounded Phase 1 backlog is prioritized.
- [ ] The team can clearly distinguish what is currently implemented, proposed, automatically tested, manually tested and still unverified.

**Phase 0 success is clarity and testability, not the number of new screens or files.** The next phase should be the smallest end-to-end improvement that proves the core learning journey works reliably for a real learner.

---

## 17. Reference sources

Official product sources reviewed on 25 October 2026. Feature availability can vary by account, region, rollout and product plan.

- Google, **Gemini Notebook for students** — source-grounded answers with citations; study materials, flashcards and quizzes: https://notebook.google/students?hl=en-US
- Google, **6 NotebookLM features to help students learn** — source-grounded study guides, customized materials and Learning Guide: https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-student-features/
- Google, **Study notebooks in the Gemini app** — diagnostic knowledge-gap checks, tailored lessons, quizzes and a skill-focused progress dashboard (published 25 June 2026): https://blog.google/innovation-and-ai/products/gemini-app/gemini-study-notebooks/
- Google, **New study tools for Gemini Notebook** — interactive learning overviews, short video overviews and expanded quiz formats (September 2026): https://blog.google/innovation-and-ai/products/gemini-notebook/new-study-tools-september-2026/
- Google, **Three new ways to study with Gemini Notebook** — updates to short video and interactive learning overviews (published 16 October 2026): https://blog.google/innovation-and-ai/products/gemini-notebook/three-tips-study-gemini-notebook/
- Google, **Guided Learning with Gemini** — step-by-step help, questions, explanations, visuals and recap/next steps: https://blog.google/products-and-platforms/products/gemini/guided-learning-google-gemini/
- Khan Academy, **Khanmigo** — tutor behavior focused on reasoning rather than simply giving answers: https://www.khanacademy.org/khanmigo
- Khan Academy Help Center, **What is self-paced Mastery?** — skill progression, course challenge and practice-linked feedback: https://support.khanacademy.org/hc/en-us/articles/360007253831-Using-self-paced-practice-and-Mastery-in-the-classroom
- Coursera Help Center, **Taking assignments** — distinction between graded, practice and honors assignments: https://www.coursera.support/s/article/learner-000001563?language=en_US

---

*End of Phase 0 blueprint.*
