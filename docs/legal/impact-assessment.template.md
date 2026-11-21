# Personal Data Protection Impact Assessment (DPIA) — Template

**Status:** Blank template — complete before high-risk processing; counsel and the PPDP/data-protection function must review.  
**Do not put learner names, guardian identity data, or private evidence links in this file.**

## A. Assessment metadata

- Assessment ID:
- Product / feature / release:
- Version and reviewed commit SHA:
- Controller/operator legal name:
- Responsible adult owner:
- PPDP/privacy function contact:
- Product/engineering owner:
- Qualified Indonesian counsel:
- Independent security reviewer:
- Assessment date:
- Next review date:
- Status: not_started / in_progress / approved_with_controls / rejected / reassessment_required

## B. Processing description

- Exact feature and user journey:
- Child age bands in scope:
- Whether children are known or reasonably likely to use/access it:
- Specific purpose(s):
- Lawful basis for each purpose and counsel rationale:
- Data categories and source:
- Data subjects:
- Processing operations and frequency:
- Systems, database tables, logs, backups, and devices:
- Recipients, processors, and subprocessors:
- Storage and support locations:
- Cross-border transfer destinations and legal mechanism:
- Retention period and deletion trigger:
- Automated decision/profiling analysis:
- Human review, contest, correction, and reset mechanisms:

## C. Necessity and proportionality

For each field and operation explain:
- Why it is necessary for the stated purpose.
- Why a less intrusive alternative will not achieve the purpose.
- Whether the feature works with less data or no persistent profile.
- Whether the data can be aggregated or pseudonymised earlier.
- Whether the purpose can be achieved without external AI or third-party sharing.
- Whether the learner can use unrelated features after refusing an optional purpose.
- How the design considers the child's best interests and age-related understanding.

Remove data fields and processing steps that cannot be justified.

## D. Child-specific and technical risk assessment

Score each risk before and after controls using a defined internal scale (for example, likelihood 1–5 multiplied by impact 1–5). This scale is an internal tool, not an official government risk classification. Include evidence and residual risk.

| Risk | People/harm | Likelihood | Impact | Initial rating | Mitigation | Residual rating | Owner/evidence |
|---|---|---:|---:|---:|---|---:|---|
| Unauthorised access / cross-account exposure | Child privacy, safety, trust | | | | Tenant isolation, least privilege, access tests | | |
| Incorrect or overconfident learner label | Self-perception, opportunity, educational harm | | | | Transparent provisional labels, correction, human review, no high-stakes decisions | | |
| Article 19 prohibited profiling | Legal and child-rights harm | | | | Counsel classification, disable unless exception and safeguards | | |
| Excessive data collection | Privacy and security exposure | | | | Minimise fields and purposes | | |
| Excessive engagement pressure | Wellbeing and autonomy | | | | No punitive streak loss, shame, ranking or daily-use pressure | | |
| AI hallucination or inappropriate output | Learning and safeguarding harm | | | | Disable by default, provider review, age-appropriate testing, reporting | | |
| Data sent to unreviewed third party | Confidentiality and transfer harm | | | | Provider allowlist, payload tests, server-side controls | | |
| Age/guardian verification failure | Child access and unlawful processing | | | | Proportionate verified process, fail-closed server gate | | |
| Retention or deletion failure | Ongoing exposure and rights harm | | | | Schedule, tested deletion, backup expiry | | |
| School/teacher overreach | Unnecessary disclosure or pressure | | | | Role-based access, transparent school contracts, minimum scope | | |

Add feature-specific risks. Assess direct harm, indirect harm, group effects, and cumulative risks.

## E. Profiling and automated processing analysis

- Does the feature identify, evaluate, or predict aspects of a child?
- Which variables, inferences, scores, tags, rankings, or recommendations are created?
- Does it operate by default?
- Is it a core feature?
- Is there a distinct active and conscious child request?
- Does counsel identify an Article 19 exception and explain why it applies?
- What is the child's best-interest rationale?
- What technical and operational safeguards prevent harm?
- Can the learner see, correct, contest, reset, or opt out where legally available?
- Are consequential decisions made solely by an automated process?
- What human review and escalation exist?

**Decision:** profiling_not_present / disabled_for_child_cohort / exception_supported_by_counsel / unresolved_do_not_enable

## F. Safeguards and verification

For every safeguard name the owner, implementation, test, evidence reference, and failure response:
- privacy-high defaults and minimum data;
- server-side age/guardian/consent verification;
- role-based access and tenant/account isolation;
- encryption, secrets, logging and monitoring;
- provider and transfer restrictions;
- deletion, retention and backup expiry;
- rights and complaint path;
- AI safety, if enabled;
- human review, contest, and correction;
- incident response and stop switch.

## G. Residual-risk decision

- Residual risks and affected age groups:
- Why remaining risk is proportionate and lawful:
- Additional controls and deadlines:
- Features that remain disabled:
- Rejection/stop triggers:
- Counsel decision and scope:
- PPDP/data-protection function advice:
- Security reviewer decision:
- Responsible adult operator decision:

Do not proceed where the assessment is incomplete, material risks are unmitigated, profiling legality is unresolved, or required approval is absent.

## H. Reassessment triggers

Reassess before material changes to purpose, age band, data fields, model/provider, algorithms, user interaction, school access, hosting region, retention, or sharing; and after incidents, complaints, new evidence of harm, or legal changes.

## I. Legal references

- UU PDP No. 27/2022, Article 34: https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf
- PP No. 17/2025, Article 7 and Article 19: https://peraturan.bpk.go.id/Download/377994/PP%20Nomor%2017%20Tahun%202025.pdf
- PP No. 33/2026, Articles 120–122 (effective 16 January 2027): https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
