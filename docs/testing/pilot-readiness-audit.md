# Pilot lesson readiness audit

Run from the repository root:

```bash
python scripts/audit_pilot_readiness.py
python scripts/audit_pilot_readiness.py --strict
python scripts/audit_pilot_readiness.py --strict --output artifacts/pilot-readiness.json
```

The read-only report checks every lesson opted into the strict Verified Question
Engine pilot. The readiness profile is chosen from the explicit lesson `kind`
field; titles are never used to infer the profile.

## Instructional lesson requirements

- Required lesson identity, title and teaching explanation.
- Presence of an authored worked example (reported as a warning).
- At least two currently verified questions.
- At least two currently verified practice-purpose questions.
- Stable skill IDs on verified questions.
- Presence of at least one verified application/reasoning question (reported as a warning).

## Assessment lesson requirements

A lesson with `kind: "assessment"` is checked as an assessment, not as an
instructional practice lesson:

- Required lesson identity, title and teaching explanation.
- At least two currently verified questions.
- At least two currently verified application/reasoning questions.
- Stable skill IDs on verified questions.
- Worked-example presence remains a warning, not an automatic failure.

This avoids requiring practice-purpose questions in a cumulative assessment
whose verified items are deliberately tagged as application/reasoning. It does
not lower the verified-content threshold: an assessment still needs at least
two verified questions and its own minimum application/reasoning coverage.

`--strict` exits with status 1 when structural errors exist. Warnings remain
visible but do not silently become blockers. On instructional lessons, missing
application items warn that transfer evidence is limited. Assessment lessons
must meet their application/reasoning minimum instead.

## What this does not establish

- Independent subject-matter review or mathematical correctness.
- Official curriculum alignment.
- Genuine transfer validity from application/reasoning labels.
- Live UI quality, save/reload reliability, device compatibility, or learner
  outcomes.

A structurally ready result means only that the static content meets this
repository-defined minimum. It is not a public-launch approval or a substitute
for human content review.
