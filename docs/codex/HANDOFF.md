# Vocogni — Codex Project Handoff

**Prepared:** 2026-10-17  
**Repository:** https://github.com/richman68899-hash/Vocogni  
**Production URL:** https://vocogniprototypev1.streamlit.app  
**Production source intended:** branch `main`, entrypoint `app.py`

This is a distilled, project-relevant handoff from prior ChatGPT work. It is not a full export of every chat or every ChatGPT memory. Use it to orient Codex, then verify every important claim against the current repository and live app.

## 1. Product and objective

Vocogni is an educational AI startup/prototype for Grade 7–9 mathematics. The current learning loop is:

**Understand → Solve → Apply → Advance**

The original design exploration included diagnosing misconceptions, conceptual explanation, practice, real-world transfer, measurement, and selecting the next step. The current prototype uses a transparent five-item diagnostic to guide initial practice and records learner activity. The diagnostic is rule-based; the product has not established that it improves learning outcomes yet.

Current course IDs and course-entry diagnostic/lesson structure:

- **Simple Fractions**: diagnostic, then Understanding Fractions, Adding Fractions, Simplifying Fractions, Real-World Challenge: Scaling a Recipe.
- **Algebra Basics**: diagnostic, then What Is a Variable?, Solving Simple Equations, Working with Negative Numbers, Real-World Challenge: Pricing a Product.
- **Word Problems**: diagnostic, then Translating Words into Math, Multi-Step Problems, Identifying Key Information, Real-World Challenge: Planning a Class Trip.

Each of the four instructional lessons in each course is intended to use:
1. Screen 1 — concept explanation
2. Screen 2 — worked example
3. Screen 3 — interactive question with feedback

Treat this as intended/current-code behavior until verified in a running browser.

## 2. Technical architecture and files

- **Streamlit** app. `app.py` is the entrypoint.
- **Auth0 / OIDC** provides login, commonly through Google. Streamlit exposes the authenticated identity through `st.user`.
- **`persistence.py`** stores and loads learner state from Supabase PostgreSQL.
- **`state.py`** owns session setup, restore/merge compatibility, dirty/save state, and autosave coordination.
- **`data.py`** stores courses, lessons, questions, diagnostics, and learning content in Python data structures.
- **`diagnostics.py`** performs explainable, rule-based scoring and pathway selection.
- **`logic.py`** holds framework-independent answer checking, progress statistics, recommendations, and related logic. Keep Streamlit imports out of this module.
- **`sections/course.py`** renders the course list/detail and lesson flow.
- **`sections/browse.py`**, **`sections/progress.py`**, and other `sections/*.py` modules render the app's sections.
- **`styles.py`** owns application CSS.
- **`tests/`** contains automated tests.
- **`README.md`** and **`docs/testing/`** contain the repository's current documentation and acceptance-test requirements.

Expected data path:
`Google → Auth0 → Streamlit OIDC/st.user → state.py → persistence.py → Supabase PostgreSQL`

The intended `learner_progress` table uses `user_id` as the authenticated user subject/key, `progress` as JSONB, and `updated_at`. Inspect `persistence.py` and the actual Supabase schema before changing assumptions.

Last documented secret names:
- `SUPABASE_URL`
- `SUPABASE_SERVER_KEY` (preferred by the current persistence code; legacy `SUPABASE_KEY` compatibility may exist)
- Streamlit `[auth]` and `[auth.auth0]` settings for OIDC

Never print or commit actual secret values. Do not conflate Auth0 login with Supabase Auth. Avoid major rewrites or premature database normalization.

## 3. Existing features and important behavior

The repository has included:
- Authenticated user sessions through Streamlit OIDC/Auth0.
- Persistent learner profile/progress, notes and settings.
- Course browsing and progress statistics.
- Five-item lesson diagnostics, prerequisite gating, outcome/weakness summaries, and pathway selection.
- Separate practice-attempt records and lesson-assessment snapshots.
- Diagnostic-first course display plus structured three-screen lesson content across all three courses.
- Save-state handling intended to persist meaningful learner changes.

Do not assume every item is fully validated in production. Confirm current implementation, test output, and live behavior.

### Progress-preservation constraints
- Existing stable lesson IDs must remain stable unless there is an explicit migration plan.
- Diagnostic results are separate from regular practice counts.
- Practice retakes should not reset a one-time diagnostic or overwrite previous attempt summaries.
- New screen checkpoints should be additive and backward-compatible with older learner records.
- A visible “Saved” indicator alone is insufficient evidence of successful database persistence.
- Multi-user isolation is important: one authenticated learner must not read another learner's progress.

## 4. Current verified repository checkpoint

As of this handoff:
- PR #7 added the diagnostic-first five-item Word Problems course and three-screen flow; it was merged.
- PR #8 generalized three-screen content and screen-progress checkpoints to Simple Fractions and Algebra Basics, and updated progress summaries; it was merged.
- The PR #8 GitHub Actions run passed Python compilation and the repository's automated unittest suite: https://github.com/richman68899-hash/Vocogni/actions/runs/39020247365
- Merge commit for PR #8: `713492f9b8c4552368f790e58a30914d68c293fc`.

**What this verification does not establish:** live browser behavior, deployment freshness, actual Auth0 login/logout success, refresh/re-login restoration from Supabase, multi-account isolation, or reliable save behavior during network failures. Verify these before claiming the app is production-ready.

## 5. Current priority and decision rules

The near-term goal is to plan the fastest credible route from the current prototype to a usable MVP. Optimize for:
- A small, coherent end-to-end learning journey that can be demonstrated.
- Reliable login, learner-specific saved progress, and recoverable save failures.
- Correct diagnostic → teaching → interactive practice → feedback → progress flow.
- Evidence that learners can use the experience and that it helps them learn.
- A demo and reproducible evidence of outcomes before adding large amounts of automation.

Avoid:
- A big-bang rewrite.
- Adding frameworks or infrastructure without a specific measured need.
- Coding a feature before defining its user value and acceptance criteria.
- Treating a feature as complete only because source code or unit tests exist.
- Over-planning; create a short, ordered, testable plan and start with the highest-risk bottleneck.

## 6. First Codex task: audit and plan only

Start by auditing the live repository, not by coding. Give Codex this prompt:

> Read `AGENTS.md`, `README.md`, and `docs/codex/HANDOFF.md`. Inspect the current Git branch/status, repository structure, current implementation, tests, current GitHub Actions workflow, and any existing acceptance-test documents. Do not assume this handoff is more current than the code.
>
> My objective is the fastest credible path from this prototype to a usable, demonstrable Vocogni MVP. First establish what already works, what is implemented but unverified, what is missing, and what is broken. Separate observed evidence, inference, and unknowns.
>
> Produce a prioritized MVP plan with no more than 4–6 phases. For each phase give: user outcome, files/modules likely affected, dependencies, acceptance criteria, tests, live verification steps, risks, and a clear definition of done. Prioritize the smallest complete learner journey and persistence reliability. Include a demo/evidence milestone. Do not invent features or deadlines; mark unresolved product decisions explicitly.
>
> **Read-only planning only:** do not modify files, install dependencies, commit, push, merge, change secrets, or deploy. End by recommending the single highest-value next phase and asking for approval before implementation.

## 7. Build and verification commands

Use the current README as the authority. The documented baseline commands are:

```bash
python -m unittest discover -s tests -v
python -m py_compile data.py diagnostics.py logic.py state.py sections/course.py sections/progress.py
```

Passing these commands is only one layer. The live acceptance pass should include:
1. Sign in and log out.
2. Run a diagnostic and inspect the saved result.
3. Move through all three screens and submit an answer.
4. Refresh and sign back in to confirm saved checkpoint and history.
5. Retake practice without resetting diagnostic results.
6. Verify a second authorized test account cannot access the first account's records.
7. Exercise failed-save/network behavior safely and confirm the app does not falsely claim the data was saved.

## 8. Keep this handoff current

When implementation decisions materially change, update this file or add a short decision note. Keep claims timestamped and evidence-based. Never put private credentials, real learner records, or unrelated personal ChatGPT memories in this repository.
