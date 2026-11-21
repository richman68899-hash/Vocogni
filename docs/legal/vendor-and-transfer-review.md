# Vendor, Processor, and Cross-Border Transfer Review

**Status:** Due-diligence procedure — no provider is approved by virtue of appearing in this document.

## 1. Vendor inventory

The repository's draft privacy notice identifies these services or browser dependencies. Their actual deployment configuration, contractual role, locations, subprocessors, and retention must be checked.

| Provider / service | Known or possible function | Data flow to verify | Current approval status |
|---|---|---|---|
| Auth0 | Authentication / OIDC | Account identifiers, identity claims, tenant logs and support access | Unverified |
| Supabase | PostgreSQL learner-state persistence | Learner profile, progress, answers, notes, settings, backups, logs, metadata | Unverified |
| Streamlit hosting/runtime | Application execution and hosting | Session data, request metadata, operational/security logs, deployed secrets | Unverified |
| Google Fonts | Browser font delivery | Browser connection metadata when font files are requested | Unverified |
| External AI provider | Optional open-ended tutoring, only if configured and enabled | Current message; up to eight selected prior AI tutoring messages if sharing is enabled; limited learning summary if sharing is enabled | Feature must remain disabled until provider is identified and approved |
| School/educator integration | Conditional future use | Learner roster, identifiers, progress or assignment data, support contacts | No approval; requires separate role/contract assessment |

Do not infer that a provider is a processor rather than an independent controller, or vice versa. Determine the role from its actual purposes, instructions, contract, and behaviour.

## 2. Minimum due diligence before data flow is enabled

For each provider, record:
- exact legal entity and service/product;
- role (processor, controller, joint controller, or other) with counsel's rationale;
- data categories, purpose, endpoints, API payloads, logs, support access, and access privileges;
- primary and backup regions, support access locations, and subprocessors;
- applicable privacy notice, data processing terms, security documentation, and contract version;
- permitted processing instructions, confidentiality, access controls, and staff obligations;
- retention, backup, deletion, return, and data-rights assistance;
- incident-notification timing, cooperation, evidence, and contact;
- audit/assurance rights and material-change notifications;
- AI model training, service improvement, human review, and abuse-monitoring settings, if applicable;
- encryption, key management, tenant isolation, vulnerability handling, and business continuity; and
- exit plan, data export, deletion verification, and replacement provider.

No checkmark is valid unless supported by the actual tenant, account, contract, configuration, and release version.

## 3. International transfer control

Do not claim all data remains in Indonesia unless every relevant storage, access, support, backup, and onward-transfer path has been verified.

Before an overseas provider receives or can access personal data:
1. map the transfer and the recipient's role;
2. determine whether a transfer outside Indonesia occurs under the applicable legal definition;
3. identify the destination country, recipient, onward recipients, data categories, and purpose;
4. obtain counsel's decision on the applicable transfer route and evidence;
5. implement the appropriate protection instrument and assessment;
6. provide required information to data subjects before the transfer;
7. record the transfer in the processing register; and
8. reassess when a region, subprocessor, contract, or purpose changes.

PP 33/2026 Articles 160–170 (effective 16 January 2027) describe the transfer framework, including adequacy, adequate and binding safeguards, and consent where the preceding routes are not satisfied. Article 164 addresses information to the data subject before transfer. Counsel must apply the exact enacted provisions and current implementing rules.

## 4. External AI provider gate

Keep external AI tutoring disabled until the operator has:
- identified the exact provider, legal entity, model, account and endpoint;
- reviewed data processing terms and the provider's role;
- confirmed training and service-improvement use, retention, abuse monitoring, human access, deletion, location and subprocessors;
- inspected and tested the exact request payload;
- minimised or removed child identifiers and unrelated context;
- assessed child-specific harms, outputs, content safety, and human escalation;
- reviewed cross-border transfers and notices;
- implemented a distinct learner choice and required guardian process; and
- recorded approval for the exact model/provider/configuration.

The repository's operator acknowledgement setting is not proof of a contract, legal review, or consent. Do not enable the feature for real child users based only on that setting.

## 5. Review triggers

Repeat due diligence before enabling a new provider, changing a model, moving regions, changing logs/retention, adding support access, adding school integration, enabling new data sharing, or changing contract terms. Immediately reassess after a provider incident or notice of a subprocessor change.

## 6. Evidence record

Keep actual contracts, security reports, region evidence, data-flow diagrams, approvals, and vendor emails in a secure adult-controlled location. The public register should contain only a non-sensitive evidence reference and review metadata. Never commit credentials, private contracts, personal data, or confidential evidence URLs to Git.

## 7. References

- PP 33/2026, Articles 160–170: https://pemerintahdigital.id/assets/resources/PP33_2026-PeraturanPelaksanaanUU27_2022_PerlindunganDataPribadi.pdf
- Official PSE registration criteria: https://pse.komdigi.go.id/panduan/kriteria-pendaftaran-pse-lingkup-privat
- Permenkominfo No. 5/2020: https://jdih.komdigi.go.id/produk_hukum/view/id/759/t/peraturan%2Bmenteri%2Bkomunikasi%2Bdan%2Binformatika%2Bnomor%2B5%2Btahun%2B2020
