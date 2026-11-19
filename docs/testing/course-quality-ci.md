# Course-quality CI gate

The `Course quality audits` workflow runs on pull requests targeting `main`,
pushes to `main`, and manual workflow dispatch.

It executes two existing read-only audits in strict mode:

- `scripts/audit_learning_core.py --strict`: course and lesson identities,
  diagnostic configuration, question-bank structure, review-registry integrity,
  duplicate question IDs, and transfer-coverage reporting.
- `scripts/audit_pilot_readiness.py --strict`: minimum structural completeness
  and reviewed-question coverage for lessons opted into the strict VQE pilot.

Both commands run even when the first one fails, so a single workflow run can
surface problems from both reports. The workflow fails if either strict audit
returns a non-zero exit code.

The JSON reports are uploaded as the `course-quality-audit` artifact for 14
days, including on audit failure when a report was successfully written.

## Interpretation

A passing audit means only that the repository-defined static checks pass. It
does **not** establish mathematical correctness, independent review, official
curriculum alignment, learner usability, genuine transfer, learning gain,
privacy compliance, or release readiness. Warnings (including legacy content
coverage) remain visible in the reports and are not silently promoted to
verified status.

This workflow supplements, rather than replaces, unit tests, live acceptance
testing, human content review, and the release gates.
