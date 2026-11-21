# Personal-Data Rights, Complaints, and Access Requests Procedure

**Status:** Operating procedure draft — adult operator and counsel must configure before use.  
**Privacy rule:** Data-rights requests must use a private, monitored channel. Do not ask learners to post personal-data requests in GitHub issues, public chats, or course comments.

## 1. Roles

- **Privacy contact / PPDP:** owns intake, case tracking, deadlines, communication, and escalation.
- **Responsible adult operator/controller:** authorises decisions and confirms legal grounds for any refusal or limitation.
- **Qualified Indonesian counsel:** advises on legal interpretation, child/guardian authority, exemptions, retention exceptions, and disputes.
- **Engineering/security:** performs scoped export, correction, restriction, or deletion and records technical completion.
- **Processors:** assist under contract and return confirmation where their systems contain the relevant data.

The privacy contact must be real and monitored before any real learner is onboarded. The current repository has no configured public contact that can be assumed operational.

## 2. Intake channels and case security

Configure a private email or secure form controlled by the adult operator. Accept requests from:
- the data subject;
- a parent or legal guardian acting for a child, after proportionate authority verification; and
- another representative where the law permits and authority is verified.

Do not collect more identity evidence than needed to verify the request. Keep identity evidence separate from exported learner data and limit access to the privacy contact and authorised reviewer.

Create a unique case ID. Do not put names, emails, account IDs, exported data, identity documents, or private evidence links in Git, issue trackers, or ordinary engineering tickets. Engineering tickets should contain only the case ID, action required, scope, and completion result.

## 3. Request workflow

1. **Receive:** timestamp receipt and capture request channel, requested right, account reference, and requested scope.
2. **Acknowledge:** tell the requester that the request is being assessed, provide the private case reference, and avoid promising an unverified deadline.
3. **Verify:** proportionately verify the data subject and, where relevant, the guardian/representative's authority. Do not use verification as an unnecessary barrier.
4. **Classify:** access, copy/export, correction, deletion, restriction/cessation, objection, consent withdrawal, information/processing explanation, portability, complaint, or other request.
5. **Check legal context:** confirm identity, age status, controller/processor roles, lawful basis, third-party data, legal retention/hold, and child-specific requirements.
6. **Scope systems:** inspect the actual systems in the processing register, including Auth0, Supabase, hosting, logs, backups, AI providers, support tools, and processors.
7. **Decide:** fulfil, partially fulfil, or refuse only with a documented legal reason. A refusal must be reviewed by the responsible adult operator and counsel where necessary.
8. **Execute:** use tested, least-privilege procedures. Update processors where required; do not promise that a user-facing export includes provider logs or backups unless verified.
9. **Respond:** explain what was done, what was not done and why, relevant data categories, any remaining retention basis, and complaint route.
10. **Close:** record dates, decision, systems searched, actions, reviewer, evidence reference, and any residual tasks. Restrict the case record itself.

## 4. Requests concerning children

PP 33/2026 Article 38 (effective 16 January 2027) states that a child or their parent/guardian may request fulfilment of the child's data-subject rights. Where the child submits a request, the controller assesses the child's capacity to understand the right; the regulation also describes when parent/guardian agreement applies and an exception for the child's rights relating to personal-data processing. Counsel must map each right and request type to the applicable rule. Do not reject every request from a child automatically, and do not assume every request can be handled solely by a guardian.

For child requests:
- use age-appropriate explanations;
- assess authority and capacity using a documented, proportionate process;
- protect the child's privacy and best interests;
- involve a guardian only where required or appropriate under the applicable rule;
- escalate safeguarding concerns to the designated adult; and
- preserve confidentiality from teachers, other learners, or family members unless disclosure is legally authorised or required.

When a learner reaches the age at which they are no longer a child, follow the documented transition procedure rather than carrying forward child permissions without review.

## 5. Processing-specific timing controls

Maintain a legal deadline matrix approved by Indonesian counsel and configure timers from the actual receipt/verification event. Do not apply one generic SLA to every right.

Known provisions to include in the matrix:
- PP 33/2026 Article 71 provides a three-times-24-hours deadline for verified correction/update requests, effective 16 January 2027.
- UU PDP Article 46 and PP 33/2026 Article 114 provide a three-times-24-hours written notification framework for personal-data protection failures, with the PP 33/2026 rule calculating from when the failure is known with certainty, reasonably and properly, once effective.
- Other request types must be checked against the applicable enacted provisions and current implementing rules; do not infer a deadline from the correction rule.

The operator should set an internal target to acknowledge requests promptly, but an internal target does not replace a statutory deadline.

## 6. Data export boundaries

An export must identify its scope and limitations. For example, a download of the current learner-state database row may not include:
- Auth0 identity-provider records;
- Streamlit or hosting provider logs;
- Supabase backups or provider-side metadata;
- session-only AI conversation records; or
- records retained separately by a third-party AI provider.

Search the full processing register and each processor's documented data stores. Do not present a partial application export as a complete legal response.

## 7. Case record template

Keep this in the secure case-management system, not this public repository:

- Case ID:
- Received timestamp and channel:
- Request type and requested outcome:
- Data subject reference:
- Child/age status:
- Requester role and authority-verification reference:
- Identity-verification method and result:
- Relevant processing purposes and lawful bases:
- Systems/processors searched:
- Legal deadline(s) and source:
- Decision and rationale:
- Execution plan and responsible reviewer:
- Processor instructions and confirmations:
- Response sent timestamp:
- Completion evidence reference:
- Residual retention/hold and review date:
- Complaint/escalation status:

## 8. Completion criteria

A request is not complete merely because a button was clicked or a database row was deleted. Confirm the action across all in-scope systems, consider caches/backups/provider copies, notify processors where required, preserve only lawful audit evidence, and communicate any unavoidable limitations accurately.

## 9. References

- UU PDP No. 27/2022: https://peraturan.bpk.go.id/Home/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf
- PP No. 33/2026, Articles 23, 37–38, 70–72 and 111; effective 16 January 2027: https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
