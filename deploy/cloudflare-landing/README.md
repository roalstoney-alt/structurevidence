# structevidence.com commercial Worker

`structevidence-commercial` serves the commercial customer plane directly at
`https://structevidence.com`. It does not proxy or mirror the public research
site at `https://structurevidence.org`.

## Public routes

- `/`, `/verify/`, `/context/`, `/decision-pack/`
- `POST /api/requests`

The public intake API writes to the existing `CUSTOMER_CASES_DB` D1 binding.
Every request starts as `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, with
no human owner, and appends a `REQUEST_SUBMITTED` event. External responses use
only `SE-REQ-*` request IDs.

The `PUBLIC_INTAKE_RATE_LIMITER` binding enforces five calls per ten-second
window per connecting IP. The API permits browser POSTs only from
`https://structevidence.com`; non-browser clients without an `Origin` header
remain supported. `www.structevidence.com` redirects permanently to the apex.

## Protected routes

- `/admin/requests/` uses `ADMIN_UI_AUD`.
- `/api/admin/*` uses `ADMIN_API_AUD`.

Both route groups validate the Cloudflare Access assertion issuer, audience,
authenticated email, and the `ADMIN_EMAILS` allowlist. Missing configuration
fails closed. Configure `TEAM_DOMAIN`, `ADMIN_UI_AUD`, `ADMIN_API_AUD`, and
`ADMIN_EMAILS` as Worker variables or secrets; `keep_vars` preserves values
managed outside this file.

## Database and deployment

The binding targets the existing database:

- name: `structurevidence-customer-cases`
- id: `aee10591-536a-47af-8ee0-957551ba2360`

```sh
pnpm install --frozen-lockfile
pnpm test
pnpm exec wrangler d1 migrations list structurevidence-customer-cases --remote
pnpm exec wrangler d1 migrations apply structurevidence-customer-cases --remote
pnpm exec wrangler deploy --dry-run
pnpm exec wrangler deploy
```

Customer data must never be copied into public CML, RDL, evidence, case, or
timeline records. Submission does not authorize research or publication.
