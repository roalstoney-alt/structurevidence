# structevidence.com commercial Worker

`structevidence-commercial` serves the commercial customer plane directly at
`https://structevidence.com`. It does not proxy or mirror the public research
site at `https://structurevidence.org`.

## Public routes

- `/`, `/verify/`, `/context/`, `/decision-pack/`
- `POST /api/requests`
- `/gaps/`, `/gaps/{gap_id}/`, `/gaps/changes/`
- `GET /api/gaps`, `GET /api/gaps/{gap_id}`
- `POST /api/gaps/{gap_id}/challenge`

The public intake API writes to the existing `CUSTOMER_CASES_DB` D1 binding.
Every request starts as `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, with
no human owner, and appends a `REQUEST_SUBMITTED` event. A versioned,
append-only consent receipt records acknowledgement of this boundary; it is not
research authorization. External responses use only `SE-REQ-*` request IDs.

Public submission requires a 20–128 character `Idempotency-Key` header. Only a
SHA-256 digest of that key is stored, scoped to a SHA-256 digest of normalized
request type and email. A matching retry returns the original safe request ID;
the same scoped key with a different normalized payload returns `409` without
disclosing the existing ID. The default retention window is 24 hours.

The `PUBLIC_INTAKE_RATE_LIMITER` binding enforces five calls per ten-second
window per connecting IP. Browser POSTs that carry `Origin` must use an allowed
origin. Non-browser clients without `Origin` remain compatible; origin checks
are CSRF defense-in-depth, not authentication.
Cloudflare Turnstile is also verified server-side before any customer, request,
event, consent, or idempotency row is written. `www.structevidence.com`
redirects permanently to the apex.

Open Evidence Gap challenges accept a public URL or document reference only;
there is no login and no file upload. `GAP_RATE_LIMIT_SALT` must be configured
as a Worker secret. The service stores only a SHA-256 IP-derived key and the
database trigger enforces five submissions per rolling ten minutes. Every new
challenge starts as `SUBMITTED` and appends a `SUBMITTED` event. It does not
change a gap, claim, case, or evidence state.

## Protected routes

- `/admin/requests/` uses `ADMIN_UI_AUD`.
- `/api/admin/*` uses `ADMIN_API_AUD`.

Authenticated gap-review APIs are:

- `GET /api/admin/gap-challenges`
- `GET /api/admin/gap-challenges/{challenge_id}`
- `PATCH /api/admin/gap-challenges/{challenge_id}`
- `POST /api/admin/gap-challenges/{challenge_id}/public-change`

Review transitions append immutable `gap_challenge_events`. Publication is a
separate explicit operation allowed only after a human reviewer moves the
challenge to the matching `STATE_CHANGED`, `NO_STATE_CHANGE`, or
`SCOPE_CLARIFIED` state. Public changes are append-only and never rewrite the
six frozen gap definitions.

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
pnpm exec wrangler secret put GAP_RATE_LIMIT_SALT
pnpm exec wrangler secret put TURNSTILE_SECRET_KEY
pnpm exec wrangler d1 migrations list structurevidence-customer-cases --remote
pnpm exec wrangler d1 migrations apply structurevidence-customer-cases --remote
pnpm exec wrangler deploy --dry-run
pnpm exec wrangler deploy
```

Before deployment, replace the `TURNSTILE_SITE_KEY` placeholder with the public
site key configured for the expected hostnames and action. The secret key is
never committed. Migration `0003_intake_hardening.sql` must be applied before
the matching Worker and front end are deployed together. Deploying the new
server alone would reject the old client; deploying the new client alone would
send fields the old server does not audit. See
`migrations/0003_intake_hardening_ROLLBACK.md` for the rollback boundary.

### Isolated local intake E2E

The local harness injects fake Turnstile and Access verification but exercises
the real Worker, migrations, D1 SQL, atomic batch, unique constraints, replay,
conflict, concurrent submission, consent rejection, and admin read-after-write.
Its Wrangler config is named `never-deploy` and is not referenced by the
production config.

```sh
SE_INTAKE_E2E_STATE="$(mktemp -d)"
pnpm exec wrangler d1 migrations apply structurevidence-customer-cases --local --persist-to "$SE_INTAKE_E2E_STATE"
pnpm exec wrangler dev -c test/wrangler.e2e.jsonc --local --persist-to "$SE_INTAKE_E2E_STATE" --port 8799 --ip 127.0.0.1
node test/run-local-intake-e2e.mjs
```

Do not add `--remote`, substitute a production URL, or deploy the local harness.

Customer data must never be copied into public CML, RDL, evidence, case, or
timeline records. Submission does not authorize research or publication.

The imported `OIL-GENESIS-001` handoff remains `PAUSED`. Gap challenges are a
separate VORTEX evidence channel: they do not authorize supplier outreach,
create OIL Provider/VCF/Demand/Outcome/Reuse records, establish OIL T0, or
advance OIL to Stage 4.
