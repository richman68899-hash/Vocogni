# Owner badge

Vocogni renders the blue owner badge beside the authenticated owner's
name in the sidebar and profile identity card. Other learner accounts do not
receive the badge.

## Identity rule

The check compares the current Streamlit OIDC `st.user["sub"]` claim against
one configured allowlisted subject. It never checks display name, profile
name, or email. If the setting is absent or the current subject is unavailable,
the check fails closed and the badge is hidden.

## Configuration

In the deployed Streamlit app, open **App settings → Secrets** and add:

```toml
VOCogni_VERIFIED_USER_SUB = "YOUR_AUTH0_USER_ID"
```

Use the exact **User ID** shown for the owner account in the Auth0 dashboard
(Users → select the owner account). For Google social logins, this is often a
provider-prefixed subject such as `google-oauth2|...`. Do not use the visible
profile name or email in place of the subject.

The same setting can be provided as an environment variable in local
development. The subject is read only for comparison and is never rendered,
logged, or written into learner progress.

## Appearance

The badge is an original inline SVG asset with no background rectangle. Its
canvas is transparent, so it works on both light and dark themes without a
white circle or image crop. The blue seal and white check remain visible in
both modes.
