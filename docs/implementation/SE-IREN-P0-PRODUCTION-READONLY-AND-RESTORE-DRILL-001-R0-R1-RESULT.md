# SE-IREN-P0-PRODUCTION-READONLY-AND-RESTORE-DRILL-001 · R0/R1 result

Observation window: 2026-10-26T23:15:00Z–2026-10-26T23:22:00Z
Scope: production metadata, aggregate counts, public GET/OPTIONS, and unauthenticated Access behavior only.

```text
PR54_HEAD = ff1083d319c4171add34191d63413a68e0fb968d
MAIN_SHA = 56f8e345ddfc697855c8eb9492dc0b49d24c6fcc
PR54_DRAFT = YES
PR54_MERGED = NO

R0_INVARIANT_SNAPSHOT = PASS
R1_PRODUCTION_READONLY = PARTIAL
PRODUCTION_WORKER_METADATA = PASS
PRODUCTION_EDGE_ROUTES = PASS_OBSERVED
PRODUCTION_CONTROL_PLANE_ROUTE_INVENTORY = BLOCKED
PRODUCTION_D1_MIGRATIONS = PASS
PRODUCTION_D1_TABLE_INFO_INDEX_FK_COUNTS = PASS
PRODUCTION_D1_FULL_DDL = BLOCKED
PRODUCTION_PUBLIC_GET = PASS
PRODUCTION_API_OPTIONS = PASS_OBSERVED_CURRENT_VERSION
PRODUCTION_ACCESS_UNAUTHORIZED = PASS
PRODUCTION_RELEASE_COMPATIBILITY = NOT_READY

R2_RESTORE_DRILL = NOT_AUTHORIZED_NOT_PERFORMED
PRODUCTION_BACKUP_RECOVERABILITY = UNKNOWN
HUMAN_PRIVACY_REVIEW = PENDING
READY_FOR_OWNER_PRODUCTION_RELEASE = NO

PRODUCTION_POST_COUNT = 0
PRODUCTION_DEPLOYMENT = NO
PRODUCTION_MIGRATION_APPLIED = NO
PR_MERGED = NO
PUBLIC_PILOT_STARTED = NO
```

## R0 — invariant snapshot

- Local branch, remote branch, and PR #54 were locked to `ff1083d319c4171add34191d63413a68e0fb968d` before observation.
- Main remained `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`.
- PR #54 remained open, mergeable, Draft, and unmerged.
- Staging continued to serve version `19f0ef29-c7c0-4cd0-b628-a68d860ec203` at 100%; no staging mutation was performed.

## Production Worker metadata

The authenticated Cloudflare control plane reported:

- Worker: `structevidence-commercial`.
- Deployment: `391419b5-b526-437b-b1d6-3e7c40d27fce`.
- Version: `d2525a27-12bc-49a6-9328-f11af90ea7d8`, 100% traffic.
- Version created: `2026-10-08T05:23:19.285972Z`.
- Deployment created: `2026-10-08T05:23:20.397785Z`.
- Compatibility date: `2026-09-12`.
- Plain-text variable names: `PUBLIC_ORIGINS`, `TEAM_DOMAIN`.
- Secret names: `ADMIN_API_AUD`, `ADMIN_EMAILS`, `ADMIN_UI_AUD`, `GAP_RATE_LIMIT_SALT`.
- D1 binding: `CUSTOMER_CASES_DB` → `aee10591-536a-47af-8ee0-957551ba2360`.
- Rate limiter: `PUBLIC_INTAKE_RATE_LIMITER` → namespace `842001`.

No environment or Secret value was printed or stored. The deployed version does not expose binding names for `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`, `TURNSTILE_EXPECTED_HOSTNAMES`, `TURNSTILE_EXPECTED_ACTION`, or the new idempotency TTL. Production Turnstile configuration is therefore not present in the current deployed version, not PASS.

The public edge confirmed `structevidence.com` is active and `www.structevidence.com` redirects to the canonical host. The exact control-plane route inventory remains `BLOCKED`: the authenticated dashboard settings surface did not expose route content through the available read-only interface, and this Wrangler version has no route-list command. Edge behavior is evidence of active hostname routing, but it is not represented as a complete control-plane route inventory.

## Production D1

Database: `structurevidence-customer-cases` / `aee10591-536a-47af-8ee0-957551ba2360`, observed in APAC.

- Migration list: `0003_intake_hardening.sql` remains pending and unapplied.
- Existing tables verified by field metadata: `customers`, `requests`, `request_events`.
- `request_idempotency` and `request_consent_receipts` returned `no such table`, consistent with unapplied 0003.
- Aggregate counts only: customers 3; requests 3; request events 5.
- Indexes: `idx_customers_email`, `idx_requests_created_at`, `idx_requests_status`, `idx_requests_customer`, `idx_request_events_request`, plus primary-key auto-indexes.
- Foreign keys: requests → customers; request events → requests.
- `PRAGMA foreign_key_check`: zero results.
- Trigger names: `request_events_no_update`, `request_events_no_delete`.

No customer row, request ID, email, note, event payload, Secret, JWT, or OTP was retrieved. Full `sqlite_master.sql` DDL retrieval was rejected by Cloudflare D1 with `SQLITE_AUTH`. Narrower read-only PRAGMA queries verified field metadata, indexes, foreign keys and aggregate counts, while a names-only query verified the two relevant trigger names. `PRODUCTION_D1_FULL_DDL = BLOCKED`, not PASS.

## Public HTTP and Access checks

| UTC | Method | Path | Status | Safe observation |
|---|---|---|---:|---|
| 2026-10-26T23:21:34.015Z | GET | `/` | 200 | 7,127 bytes; SHA-256 `7cc7dbc365d9cd9b2527e473563ea532bf09c4fc3f3997fd493fc84e1743bf02` |
| 2026-10-26T23:21:34.554Z | GET | `/verify/` | 200 | 7,877 bytes; SHA-256 `cc99bbe5cc46458df6758def9d5dada35d2d7aae1cccad0372141364d03b5401` |
| 2026-10-26T23:21:34.630Z | GET | `/context/` | 200 | 7,268 bytes; SHA-256 `0655411efa695a2c1ecf63349a8ccd55105b99f1aec1ab6db7c659cf4dbc2eea` |
| 2026-10-26T23:21:34.699Z | GET | `/decision-pack/` | 200 | 7,755 bytes; SHA-256 `cefce2a3ea6ea63d93b7f8cfd2de12a7bc7b7fe57bf229949092850eb5a0be9d` |
| 2026-10-26T23:21:34.760Z | GET | `/assets/app.js` | 200 | 3,727 bytes; SHA-256 `0bd3bf36bbc62a3f61d29afd027c4bf5978e7600d9583312f35b93dde2342524` |
| 2026-10-26T23:21:35.492Z | OPTIONS | `/api/requests` | 204 | origin allowed; methods `POST, OPTIONS`; headers currently only `content-type` |
| 2026-10-26T23:21:35.556Z | GET | `/api/admin/requests` | 302 | redirected to the Access login origin/path; query removed from report |
| 2026-10-26T23:21:35.731Z | GET | `/admin/requests/` | 302 | redirected to the Access login origin/path; query removed from report |

`www.structevidence.com/` returned 308 to `https://structevidence.com/` during the same window.

The current production OPTIONS response does not allow `idempotency-key`, and the deployed version has no Turnstile bindings. This is the expected old production plane, but it is not compatible with the PR #54 hardened frontend/API contract. Worker, migration, Turnstile, Access and frontend must remain a separately authorized sequenced release; no component may be deployed alone.

## Privacy, prohibited actions, and blockers

- Customer rows retrieved: NO.
- Private identifiers retrieved: NO.
- Secret values, JWT, OTP or auth headers retrieved: NO.
- Only aggregate row counts and schema metadata were recorded.
- Backup/export: NOT RUN.
- Restore target: NOT CREATED.
- Migration apply: NOT RUN.
- Worker deployment: NOT RUN.
- Production POST: 0.
- PR merge/public Pilot: NOT RUN.

Remaining blockers before any owner production release decision:

1. exact production control-plane route inventory remains unavailable through the current read-only interfaces;
2. full remote DDL text retrieval is blocked by `SQLITE_AUTH`;
3. production Turnstile sitekey/secret/hostname/action bindings are absent from the deployed version;
4. production OPTIONS does not yet allow `idempotency-key`;
5. R2 recoverability drill is not authorized and production backup recoverability remains UNKNOWN;
6. human privacy/legal review remains PENDING.

This result authorizes nothing beyond review of the sanitized R0/R1 evidence.

## Validation

- Production report guard: 2/2 PASS.
- Cloudflare landing/Worker suite: 58/58 PASS.
- Repository Python suite: 41 tests; 30 pass and 11 pre-existing failures; 0 new failures.
- Scripts Python suite: 520 tests; 470 pass, 39 pre-existing failures and 11 pre-existing errors; 0 new failures or errors attributable to this report-only change.
- Public record drift: PASS.
- Internal link audit: PASS; 0 orphan pages, 0 broken internal links, 0 cases without state, 0 evidence without parent.
- `git diff --check`: PASS.
- `NEW_REGRESSION_COUNT = 0`.
