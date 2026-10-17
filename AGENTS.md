# Codex Instructions for VOCogni

## Purpose
VOCogni is a Grade 7–9 mathematics learning prototype. Its product loop is **Understand → Solve → Apply → Advance**. The current codebase is the source of truth; plans and previous AI summaries are context, not proof that a feature works.

## Before substantial work
- Read `README.md` for the repository map and current verification commands.
- Read `docs/codex/HANDOFF.md` for project decisions, known state, constraints, and the next planning task.
- Inspect the actual implementation and Git status before proposing changes. For narrow tasks, read only the files relevant to that task rather than loading every document.

## Architecture boundaries
- `app.py` is the Streamlit entrypoint.
- `data.py` owns course/lesson/question content as data, not UI.
- `diagnostics.py` owns transparent, rule-based diagnostic scoring and pathway selection. Do not describe it as a trained or validated AI model.
- `logic.py` contains framework-independent progress and answer logic; keep Streamlit imports out of it.
- `sections/*.py` owns UI sections and lesson flow.
- `state.py` coordinates session/durable state and autosaving.
- `persistence.py` handles authenticated learner-state persistence to Supabase.

Keep Auth0 OIDC separate from Supabase Auth. The authenticated Streamlit identity is the basis for per-user learner data. Preserve this architecture unless a measured requirement justifies a change and the user explicitly approves the plan.

## Preserve learner data
- Do not reset, rename, or discard existing lesson IDs, learner records, diagnostic results, completed lessons, attempts, assessments, notes, or settings just to simplify a change.
- Evolve the existing progress JSON compatibly. Test old/missing fields as well as new records.
- A local UI state change is not evidence of a successful database save. Verify persistence and report save errors accurately.
- Never put credentials, OAuth secrets, Supabase keys, tokens, or real learner data in source control, logs, tests, or documentation.

## Workflow
1. Inspect current code, working tree, related tests, and deployment state.
2. For a substantial feature, propose a small phased plan with measurable acceptance criteria before implementation.
3. Prefer the smallest change that validates the product need. Do not add frameworks, services, normalized tables, or automation merely because they are available.
4. Make focused changes, add/update tests, and run the repository's documented commands.
5. Report what changed, exact tests run and outcomes, unverified behavior, risks, and the next decision.
6. Do not commit, push, merge, alter production settings, or deploy unless explicitly asked.

## Verification
From the repository root, use the current README commands, including:
```bash
python -m unittest discover -s tests -v
python -m py_compile data.py diagnostics.py logic.py state.py sections/course.py sections/progress.py
```
These checks do not prove that live Streamlit UI, Auth0 login/logout, or Supabase persistence works. Keep automated test evidence separate from live acceptance evidence.
