# Proposed OAuth implementation

**Status: Not implemented — pending Reddit Data API approval.**

The project will not attempt to create or use Reddit OAuth credentials until Reddit authorizes the application.

## Authentication selection

The final OAuth grant type must match Reddit's approval and current developer documentation. App-only authentication must not be assumed to provide access to all public, adult, or otherwise restricted posts. If Reddit requires a user-authorized flow, use only the permitted authorization flow and approved scopes.

Password-grant authentication and browser-cookie reuse are not part of this proposal.

## Secret management

Production secrets will be injected through the server's secret-management mechanism or protected environment variables. They will not be committed to this repository.

Expected configuration names may be finalized during implementation; no values belong in source control. Tokens should be kept in memory or in a protected store only when necessary.

## Token lifecycle

After approval and implementation:

1. Obtain tokens through the approved OAuth flow.
2. Validate successful token responses and expiry metadata.
3. Refresh or reacquire tokens only using the permitted grant.
4. Handle 401/403 responses explicitly; do not loop or attempt access-control workarounds.
5. Redact Authorization headers and credentials from logs.
6. Revoke/delete stored authorization material when access is withdrawn or no longer needed.

## Verification before release

- Confirm API access is approved for this exact application and use case.
- Verify token acquisition using a non-sensitive permitted test.
- Verify a public post response.
- Verify any restricted-content behavior only within the permission Reddit explicitly grants.
- Verify API rate-limit handling.
- Verify credential redaction and absence of secrets in Git history.
- Verify end-to-end Telegram delivery only for content the API and media host allow.

A successful token response alone is not proof that every post or media host is accessible.
