# External AI tutoring — operator enablement gate

**Status:** Implemented in source; operator configuration and provider review remain deployment responsibilities.

## Default behavior

External AI tutoring is disabled unless the server operator explicitly enables it. Supplying a base URL, model name, and API key is not sufficient.

Choose one server-side configuration:

Environment:
`VOCogni_ENABLE_EXTERNAL_AI_TUTORING=true`

or Streamlit secrets:
```toml
[llm]
enable_external_ai_tutoring = true
base_url = "https://your-approved-provider.example/v1"
model = "your-approved-model"
api_key = "server-side-secret"
```

The `[llm].enable_external_ai_tutoring` secret takes precedence over the environment flag. Only the explicit truthy values `true`, `1`, `yes`, and `on` enable the environment setting. Missing, malformed, or unreadable configuration fails closed.

## Two independent controls

1. **Operator gate:** enables the feature for the deployment.
2. **Learner session opt-in:** a learner separately enables it in the active session.

Both are required before an external request can be made. Removing the operator gate during a session clears the previous learner opt-in on the next rerun.

## Important limitations

This is a technical kill switch, not an age-verification system, parental-consent workflow, legal basis, or proof that a provider is safe for children. Do not enable external tutoring for the Grade 7–9 cohort until the responsible adult operator has completed the applicable provider, privacy, safeguarding, consent, and legal review and verified the exact production configuration. Local Study Guide commands continue to work while the external feature is disabled.
