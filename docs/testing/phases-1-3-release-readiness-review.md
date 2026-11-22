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

**Validation status:** These changes are committed to the PR branch. GitHub Actions must run on the PR commit; I have not executed the suite locally in this environment. Do not interpret the fixes as a verified green build until the PR workflows complete.

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

## PR acceptance and follow-on order

1. Review this PR and wait for its CI runs.
2. If green, merge the test repair only after inspecting the workflow results.
3. Separately create/track Phase 2 content-review work; keep question statuses honest until qualified review is complete.
4. Separately track Phase 3 implementation/evidence. Do not unlock real learners based solely on this report or the repository's static audits.
5. Phase 4 independent learner acceptance can start only after the appropriate adult-led legal, safeguarding, and infrastructure gates are satisfied.

## Explicit limitations

This review did not access the live production environment, inspect provider dashboards or secrets, conduct a penetration test, run browser/device acceptance, verify consent records, inspect lawyer advice, or independently review course mathematics. These remain unresolved release evidence requirements.
