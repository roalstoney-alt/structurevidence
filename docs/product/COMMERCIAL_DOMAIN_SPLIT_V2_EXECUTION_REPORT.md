# StructureEvidence Commercial Domain Split V2 — Execution Report

Date: 2026-09-23
Project: `STRUCTEVIDENCE_COMMERCIAL_DOMAIN_SPLIT_V2`

## Implemented boundary

- `structurevidence.org` remains the public research, method, evidence, and case plane.
- `structevidence.com` is served directly by `structevidence-commercial` as the commercial landing, intake, Decision Pack, and protected review plane.
- The `.com` homepage is not proxied from `.org` and contains only the three requested commercial offers.
- Commercial CTAs on the `.org` public surface now cross to `.com`; no customer-private parameters are passed into `.org` URLs.

## Intake and security

- `POST /api/requests` persists customer and request records plus the append-only `REQUEST_SUBMITTED` event in the existing D1 database.
- Defaults remain `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, and `human_owner = NULL`.
- Browser CORS is restricted to `https://structevidence.com`.
- Cloudflare rate limiting is bound at 5 requests per 10-second window per connecting IP; rejected requests return `429` and `Retry-After: 10`.
- Admin UI and API validate separate `ADMIN_UI_AUD` and `ADMIN_API_AUD` values. Missing Access configuration fails closed.
- CSP, nosniff, referrer, permissions, and frame protections are emitted by the Worker.

## Preservation boundary

No CML canonical record, RDL record, public evidence store, timeline record, or publication-control record was modified. The 800V evidence content is unchanged; only commercial CTA destinations changed.

## Production steps

The existing D1 database was verified, migration `0001_customer_intake.sql` was applied remotely, and the `customers`, `requests`, and `request_events` tables were confirmed.

- Worker immutable ID: `8fd8b52971a04a92b01584a22469ca69`
- Deployment version ID: `5cb2d399-58eb-4156-94ff-2c4b68aad5b2`
- Synthetic request: `SE-REQ-548117521288458EA050`
- Smoke result: HTTP 201; `CUSTOMER_PRIVATE`; `NOT_AUTHORIZED`; `REQUEST_SUBMITTED` confirmed.
- Cleanup state: request retained and marked `CLOSED`; append-only `CASE_CLOSED` event notes `INTERNAL_TEST`.
- Access state: configuration variables were not present at deployment; admin routes returned HTTP 503 and remained fail-closed.
