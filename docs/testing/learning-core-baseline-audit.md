# Learning Core Baseline Audit

Run this read-only audit from the repository root:

```bash
python scripts/audit_learning_core.py
python scripts/audit_learning_core.py --output artifacts/learning-core-audit.json
python scripts/audit_learning_core.py --strict
```

The audit combines the existing Verified Question Engine, diagnostic validator,
math skill taxonomy and transfer-coverage audit. It reports:

- Course and lesson inventory.
- Unique question counts and verification-status counts.
- Verified question distribution by purpose, difficulty and skill.
- Question-bank review issues and duplicate-ID conflicts.
- Diagnostic configuration errors.
- Registry metadata errors.
- Cross-lesson application coverage by course/skill.

## Interpreting results

- `verified` means the item currently passes the repository's VQE verification
  contract. It is not a guarantee that an independent subject-matter expert has
  rechecked it during this audit.
- `legacy` means no current VQE review record exists. It is a warning, not
  automatically a structural failure.
- `needs_review` means the item fails a current structural or review-contract
  check and should not be treated as verified.
- Transfer coverage is a metadata inventory. It does not establish that an
  application question is novel, appropriately difficult, or a valid measure
  of transfer.

The report deliberately does not claim mathematical correctness, diagnostic
reliability, learning gains, live UI correctness, or persistence correctness.

The script is read-only. It does not modify learner records, course content,
the verification registry, or the database.
