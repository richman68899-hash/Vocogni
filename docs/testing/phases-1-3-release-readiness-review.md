# Small-Batch Release Readiness Review — Phases 1–3

**Review baseline:** `bdf2e2d8a1fbe920afc1592d30f90254ceab1644`  
**Review date:** 2026-11-22  
**Scope:** Repository static review and CI evidence. This is not a live deployment, security penetration test, independent mathematics review, or legal opinion.

## Executive decision

**Real-learner release remains blocked.** This change fixes two test-suite defects and adds a regression assertion. It does not mark curriculum questions as independently reviewed, claim production privacy/security controls are proven, or enable child access.

## Phase 1 — Engineering stabilization

### CI defects confirmed from the latest GitHub Actions run

- `tests/test_diagnostics.py` contained a literal escaped newline between two assertions, causing a SyntaxError and preventing that test module from importing.
- `tests/test_local_developer_mode.py` correctly tested overwrite protection, but the second attempted backup used an incomplete snapshot. Production validation rejects incomplete snapshots before reaching the overwrite-protection path. The regression now passes a complete snapshot to test overwrite refusal and separately asserts that incomplete snapshots are rejected.
- `test_diagnostics.py` contained two definitions of `deliberately_wrong_answer`. The redundant second definition was removed so there is one helper implementation.

### Fixes in this PR

1. Repair the malformed diagnostics test line.
2. Remove the duplicate helper.
3. Make the backup-overwrite test reach the intended overwrite guard using a valid snapshot.
4. Add an explicit regression test for incomplete-snapshot rejection.

**Validation status at the #207 merge:** The Python test suite, diagnostics workflow, and AI prototype checks passed on the PR head. After merge, the Python test suite and diagnostics workflow also passed on `main` at merge commit `8e9c9eb5c34ee53524ee2294b819b0e47f0154ac`. The course-quality workflow did **not** pass; its exact result is recorded below. I did not execute the suite locally in this environment.

## Phase 2 — Learning-content readiness

### Decision: no question was falsely promoted to “verified”

The strict audit failure is a content-review failure, not a Python defect. The current audit reports that Adding Fractions has no verified question records and therefore fails the pilot coverage requirements.

Recommended first pathway for review:
- Algebra Basics — What Is a Variable?
- Algebra Basics — Solving Simple Equations

The second lesson currently has practice coverage but no verified application/reasoning questions, so it needs at least two independently reviewed application/reasoning items if the pathway's transfer claim requires that coverage. Do not use story-text changes alone as transfer.

### Required content review evidence

For every included item, reviewer evidence should identify:
- stable question ID and version;
- skill/objective tested;
- correct answer and any accepted equivalents;
- calculation, units, tolerance and partial-credit rules where applicable;
- misconception/distractor validity;
- learner level/difficulty;
- purpose (practice, application or reasoning) justified by the actual task;
- review date and independent reviewer.

The structural audit is not a substitute for a qualified mathematics teacher. This phase is **prepared but not complete** until a qualified reviewer has examined the actual content and any new items and the strict audit passes for the declared pilot scope.

## Phase 3 — Privacy, security and operational release controls

### P0 release blockers requiring accountable adult operator and qualified Indonesian counsel

- Determine the legal operator/data-controller arrangement and identify accountable adult owner.
- Resolve intended age band, age-appropriate feature risk, child-user verification, guardian-authorisation verification, and applicable child-profiling restrictions.
- Determine and complete applicable risk assessment/DPIA, notices, registration and other legal requirements.
- Keep the public/real-learner release gate closed until written approval for the exact release configuration.

### P0 technical evidence that is not established by source review

- Independently verify production database grants and Row Level Security, server-side credentials, and cross-account isolation.
- Confirm Auth0 tenant settings, claims, session/callback/logout behavior and account-switching boundaries.
- Confirm hosting, deployed SHA, environment secrets, logging, backups, data regions, subprocessors and support-access locations.
- Test recovery from a backup and rollback of the deployed build.
- Confirm retention/deletion across application data, provider logs, backups, and any third-party AI provider; application-level row deletion alone is not proof of complete deletion.
- Configure and test a real, monitored support/reporting contact and staffed incident-response procedure.
- Keep optional external AI tutoring disabled for the first controlled cohort until provider-specific data-flow, contract, safety, and legal reviews are completed.

### Existing controls — useful, but not release evidence

- The internal preview release gate uses an OIDC-subject allowlist. It is not a child age-verification or guardian-consent system.
- Profiling safeguards check gate conditions, but those conditions must be backed by trusted server-side evidence and cannot be satisfied by a client-controlled boolean.
- Legal and release checklists are documentation and audit tooling. A green structural/documentary audit does not prove the contracts, consent evidence, provider configuration, or operational procedures exist.

### Evidence to collect (private adult-controlled workspace)

Store evidence references—not learner identifiers, identity documents, private contracts, credentials, or sensitive provider screenshots—in the repository:
1. legal review/decision log and approvals;
2. data-flow and processing register;
3. provider and transfer assessment;
4. security-review report and isolation test results;
5. retention/deletion test evidence;
6. incident tabletop and support-contact readiness;
7. release SHA and rollback evidence.

## Verified CI outcome for PR #207 (2026-11-22)

PR #207 was merged into `main` as `8e9c9eb5c34ee53524ee2294b819b0e47f0154ac`.

| Workflow | PR-head result | Post-merge `main` result |
|---|---|---|
| Python tests | Pass | Pass |
| Vocogni diagnostics checks | Pass | Pass |
| AI prototype checks | Pass | Not triggered by the `main` push workflow configuration |
| Course quality audits | **Fail** | **Fail** |

Evidence:
- [PR Python tests](https://github.com/richman68899-hash/Vocogni/actions/runs/45033322360)
- [PR diagnostics checks](https://github.com/richman68899-hash/Vocogni/actions/runs/45033322341)
- [PR AI prototype checks](https://github.com/richman68899-hash/Vocogni/actions/runs/45033322364)
- [PR course-quality audit](https://github.com/richman68899-hash/Vocogni/actions/runs/45033322303)
- [Post-merge Python tests](https://github.com/richman68899-hash/Vocogni/actions/runs/45033504616)
- [Post-merge diagnostics checks](https://github.com/richman68899-hash/Vocogni/actions/runs/45033504538)
- [Post-merge course-quality audit](https://github.com/richman68899-hash/Vocogni/actions/runs/45033504519)

The course-quality job produced these results:
- Learning-core audit: 7 courses, 49 lessons, 212 unique questions, 0 structural errors, 152 warnings. This audit exits successfully in strict mode because the warnings are not classified as errors.
- Pilot readiness audit: 11/12 lessons structurally ready, 2 errors, 6 warnings.
- Both pilot-readiness errors are in `fractions/fractions_l2` (Adding Fractions): 0 verified questions and 0 verified practice questions, against requirements of at least 2 of each.
- The lesson has 3 `ai_reviewed` items. They are not counted as `verified`, correctly preserving the distinction between AI-assisted review and the VQE verified status.

The failing workflow is a valid product-quality gate, not a test-runner problem. Do not make it green by weakening strict checks, relabelling AI-reviewed items as verified, or silently excluding a lesson from strict retrieval. The current `question_engine.PILOT_LESSONS` set contains 12 lessons across five courses. The Algebra Basics pathway is a possible narrow first pathway, but changing the actual pilot scope requires a deliberate product decision and regression tests proving out-of-scope lessons are not presented as pilot-ready.

## Follow-on order

1. Keep the two Phase 1 test repairs from #207; their Python and diagnostics CI checks pass after merge.
2. Review [PR #208](https://github.com/richman68899-hash/Vocogni/pull/208), which implements the concurrent synthetic-backup no-clobber fix and adds a regression test. Do not treat it as validated until its CI checks pass.
3. Phase 2 remains open: obtain qualified independent mathematics review for the intended pilot scope; create or revise application/reasoning items where transfer is claimed; rerun the strict audit without falsifying verification status.
4. Phase 3 remains open: an accountable adult operator and qualified Indonesian counsel must decide legal eligibility, child profiling, age assurance, guardian authorisation, required assessments/notices/registrations, and feature scope. An independent technical reviewer must verify production identity, database isolation, secrets, providers, retention/deletion, backup restore, monitoring, incident response, and rollback.
5. Do not unlock real learners or declare release-ready until the exact release configuration has evidence for all required gates. Phase 4 learner acceptance starts only after those adult-led legal, safeguarding, and infrastructure gates are satisfied.

## Explicit limitations

This review did not access the live production environment, inspect provider dashboards or secrets, conduct a penetration test, run browser/device acceptance, verify consent records, inspect lawyer advice, or independently review course mathematics. These remain unresolved release evidence requirements.
