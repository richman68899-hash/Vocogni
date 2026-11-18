# Pilot lesson readiness audit

Run from the repository root:

```bash
python scripts/audit_pilot_readiness.py
python scripts/audit_pilot_readiness.py --strict
python scripts/audit_pilot_readiness.py --strict --output artifacts/pilot-readiness.json
```

The read-only report checks every lesson opted into the strict Verified Question
Engine pilot:

- Required lesson identity, title and teaching explanation.
- Presence of an authored worked example (reported as a warning).
- At least two currently verified questions.
- At least two currently verified practice-purpose questions.
- Stable skill IDs on verified questions.
- Presence of at least one verified application/reasoning question (reported as a warning).

`--strict` exits with status 1 when structural errors exist. Warnings remain
visible but do not silently become blockers; a lesson without an application
item may still be structurally complete, while its transfer coverage remains
limited.

## What this does not establish

- Independent subject-matter review or mathematical correctness.
- Official curriculum alignment.
- Genuine transfer validity from application/reasoning labels.
- Live UI quality, save/reload reliability, device compatibility, or learner
  outcomes.

A structurally ready result means only that the static content meets this
repository-defined minimum. It is not a public-launch approval or a substitute
for human content review.
