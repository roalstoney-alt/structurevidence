# Production release record — `.com` legal remediation

## Authority and scope

- Action: `DEPLOY_COM_LEGAL_REMEDIATION_AND_MIGRATE_D1`
- Owner content approval: `YES`
- `.com` production deployment approval: `YES`
- D1 migration 0003 approval: `YES`
- `.org` publication included: `NO`
- Counsel review: `PENDING`
- Operator facts: pending facts remain unconfirmed; no compliance certification is asserted.
- Release source: `9d25cfea1b3593d5a0a215550273e67deeb82035`
- PR: `https://github.com/roalstoney-alt/structurevidence/pull/15` (draft, head verified at release source)

The release used an isolated worktree and did not merge PR #15, change `main`, publish `.org`, edit monitoring tasks, or touch the original dirty checkout.

## Preflight

- Cloudflare OAuth account and Worker write/D1 permissions: verified without displaying credentials.
- Worker: `structevidence-commercial`.
- Production D1: `structurevidence-customer-cases`, ID `aee10591-536a-47af-8ee0-957551ba2360`.
- D1 reported region: `APAC`; jurisdiction: `null`; read replication: `auto`. These are observed provider values, not a new public location commitment.
- Pre-release Worker version: `5a175eb5-c57b-483c-9d58-ab52c0de3a59` (retained as the application rollback target).
- Preserved secret names: `ADMIN_API_AUD`, `ADMIN_EMAILS`, `ADMIN_UI_AUD`, `GAP_RATE_LIMIT_SALT`; values were not read or recorded.
- Bindings verified: D1, rate limiter `842001`, `PUBLIC_ORIGINS`, `TEAM_DOMAIN`, two custom domains.
- Applied migrations before change: 0001 at `2026-09-23 15:24:45`, 0002 at `2026-10-05 16:55:06`; 0003 was pending.
- Existing event-note review used aggregate counts only: two `CASE_CLOSED` rows with non-empty notes. No note text was queried, copied or changed.
- Worker tests: 34/34 PASS. Focused legal-boundary tests: 6/6 PASS. Wrangler dry-run: PASS.
- Public release copy was checked for internal placeholders and unverified guarantees: PASS.

## Recovery preparation

- Pre-migration D1 Time Travel bookmark: captured and re-resolved for `2026-10-08T05:21:35Z`.
- Exact bookmark and rollback metadata are stored only in an access-restricted, non-Git file (`0600`) outside the repository.
- Schema-only pre-migration export: completed outside Git with mode `0600`, 5,894 bytes, SHA-256 `f9889f13c7345502aa6909ba280d61015600eed53408d6b1ab1143153b225376`.
- Private recovery record SHA-256: `2338a17f388b0ac33215615264d43c8c699c00bf69b4b5eb7d954401ecaf66fa`.
- Restore command syntax and bookmark resolution were verified. A destructive production restore was intentionally not executed.
- Database rollback limit remains explicit: reverting the Worker does not remove migration 0003; after records exist, dropping the new tables is not an acceptable rollback.

## D1 migration 0003

- Start: `2026-10-08T05:21:36Z`
- End: `2026-10-08T05:21:43Z`
- Result: `APPLIED`
- Ledger timestamp: `2026-10-08 05:21:43`
- Post-check: no pending migrations.
- Verified objects: `request_notices`, `request_private_context`, `idx_request_private_context_request`, `request_private_context_no_update`, `request_private_context_no_delete`.
- Existing protections retained: `request_events_no_update`, `request_events_no_delete`.
- Columns/defaults for notice and private-context tables were checked from remote schema metadata.
- No old event note, historical customer record, evidence state or gap state was deleted or rewritten.

## Worker release

- Deploy start: `2026-10-08T05:23:12Z`
- Deploy end: `2026-10-08T05:23:28Z`
- Active deployment created: `2026-10-08T05:23:20.397Z`
- Worker version: `d2525a27-12bc-49a6-9328-f11af90ea7d8` (version number 27)
- Tag: `legal-remediation-9d25cfe`
- Deployment message records full source SHA.
- Upload: 175.11 KiB; gzip 44.13 KiB; startup 3 ms.
- Production traffic allocation: 100% to the new version.
- Secrets, D1 binding, rate limit, origins, Access domain and security headers remained present.

## Production acceptance

### Public content and routing

- Apex: HTTP 200 with expected production body.
- `www`: HTTP 308 to `https://structevidence.com/`.
- `/en/`, `/zh-cn/`, `/es/`: HTTP 200 with their expected localized headline/body.
- `/privacy/`, `/terms/`, `/pricing/`, `/deliverables/`, `/verify/`, `/context/`: HTTP 200 and expected released wording.
- Public Gap API: HTTP 200, six gaps.
- Content assertions include the versioned notice, separate required privacy/confidentiality checkboxes, correction-without-repurchase rule, new-research boundary, non-retroactivity and no invented retention/location guarantee.
- No `TODO`, `TBD`, internal `NEEDS_*` marker or placeholder was found in the checked production pages.

### API and security behavior

- Invalid notice version: HTTP 400, no record created.
- Missing acknowledgement: HTTP 400, no record created.
- Security headers verified: CSP, Permissions-Policy, Referrer-Policy, `nosniff`, `DENY` framing.
- Allowed same-origin submission returned the expected CORS origin.
- Unauthenticated admin request: Cloudflare Access HTTP 302 challenge; no admin data returned.
- Admin positive path: `NOT_VERIFIED` because no Access administrator JWT/service token was available in the release CLI. Access was not bypassed and secret values were not inspected.
- Successful single submission and absence of a protection-configuration error establish that the configured intake rate-limit binding was active; production was not intentionally flooded.

### Authorized synthetic intake

- Request ID: `SE-REQ-56431168BA504BC5A8DA`
- Created: `2026-10-08T05:32:00.396Z`
- HTTP: 201
- Status: `SUBMITTED`
- Privacy class: `CUSTOMER_PRIVATE`
- Research authorization: `NOT_AUTHORIZED`
- Notice version: `2026-10-08`; both required acknowledgements recorded as 1.
- Publication authorization: 0; marketing consent: 0.
- Exactly one private-context row contains both synthetic markers.
- Append-only submission event has a null note and contains neither private marker.
- Public response omitted private context; public request paths returned 404; public pages and Gap API contained neither the request ID nor the private marker.
- The record is clearly labeled synthetic in its submitted fields. It remains `SUBMITTED`/`NOT_AUTHORIZED`: no Access-admin credential was available to perform the positive-path status marking, and no direct D1 update was used to bypass the audit path.

## Final release state

- D1 0003: `APPLIED_AND_VERIFIED`
- `.com` Worker: `DEPLOYED_AND_CONTENT_VERIFIED`
- Private-context isolation: `PASS`
- Admin negative path: `PASS`
- Admin positive path: `NOT_VERIFIED`
- Rollback: `NOT_EXECUTED` (no critical failure found)
- `.org` deployed by this task: `NO`
- Monitoring tasks changed: `NO`
- Overall: `PARTIAL` only because the Access-authenticated positive admin path could not be exercised; no production rollback condition was observed.
