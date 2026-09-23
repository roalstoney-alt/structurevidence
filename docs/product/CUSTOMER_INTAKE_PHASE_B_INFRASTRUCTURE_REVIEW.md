# Customer Intake Infrastructure — Phase B Review

Date: 2026-09-23
Entry SHA: `3f78f740aad224fa991a09a13046906846bbe571`

## Architecture decision

The existing `structevidence-landing` Worker can safely retain its public proxy behavior while routing `/api/requests`, `/api/admin/*`, and `/admin/requests/*` internally. No framework replacement is required.

The GitHub Pages site remains the public content origin. Verify and Context forms submit JSON to `https://structevidence.com/api/requests`; the Worker restricts CORS to the configured public origins.

## Prepared controls

- D1 binding named `CUSTOMER_CASES_DB` with an explicit placeholder database ID.
- Versioned migration creating `customers`, `requests`, and `request_events` only.
- Database constraints for request status, privacy class, and research authorization.
- Database triggers preventing update or deletion of event history.
- Non-sequential cryptographic external request/event/customer identifiers.
- 64 KiB request-body limit, strict content type, origin allowlist, field allowlists, normalization, length limits, and server-side validation.
- Public responses expose only request ID, status, and creation time.
- Admin routes validate the Cloudflare Access JWT signature, issuer, audience, and an explicit administrator email allowlist.
- Material administrative changes update the request and append events in one D1 batch.
- No autonomous research authorization or escalation.
- No file storage.

## Configuration gate

The repository does not contain the Cloudflare account's Access team domain, application audience tag, administrator allowlist, or a created D1 database ID. Placeholder values intentionally keep the admin route closed and prevent a production-ready binding claim.

Status: `AUTH_CONFIGURATION_REQUIRED`.

## Manual Cloudflare actions

1. Create D1 database `structurevidence-customer-cases`.
2. Replace the all-zero D1 database ID in `wrangler.jsonc`.
3. Create a Cloudflare Access self-hosted application protecting the exact admin path plus `/admin/requests/*` and `/api/admin/*`.
4. Configure an identity-provider policy limited to approved human reviewers.
5. Set `TEAM_DOMAIN`, `POLICY_AUD`, and `ADMIN_EMAILS` to reviewed values.
6. Apply `0001_customer_intake.sql` remotely.
7. Configure an appropriate WAF/rate-limiting rule for public POST submissions.
8. Re-run tests and dry-run, then perform an explicit human deployment review.

No remote resource or Access policy was created or modified in this run.
