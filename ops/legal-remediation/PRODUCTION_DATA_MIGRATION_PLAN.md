# Production data migration plan

Status: **PLANNED — NOT AUTHORIZED OR EXECUTED**

Target: `deploy/cloudflare-landing/migrations/0003_legal_boundary_notices.sql` after already-applied `0001` and `0002`

Data rule: use synthetic data for rehearsal; do not read or copy unrelated customer content.

## What migrations 0001–0003 do

| Migration | Actual effect | Compatibility and risk |
|---|---|---|
| `0001_customer_intake.sql` | Creates `customers`, `requests`, append-only `request_events`, indexes and update/delete-blocking event triggers. | Existing production foundation. `request_events.note` can contain legacy narrative; append-only triggers intentionally prevent in-place cleanup. |
| `0002_open_evidence_gaps.sql` | Creates gap challenges, append-only challenge/public-change histories, rate-limit trigger and indexes. | Independent of request notice/private-context changes; must not be rewritten by this release. |
| `0003_legal_boundary_notices.sql` | Adds one versioned notice/acknowledgement row per request and an append-only private-context table. | Additive to existing tables. The new Worker requires these tables for new submissions. Raw SQL is not independently idempotent; Wrangler relies on the `d1_migrations` ledger. Dropping these tables after use would destroy new records and is not an acceptable rollback. |

Migration 0003 does **not** backfill old requests, inspect or move legacy event notes, delete data, change gap state, or alter existing append-only triggers.

## Read-only production preflight

Run only after separate production-account and migration authorization. Record outputs without customer rows or secrets.

1. Confirm the intended account, database binding/name and currently deployed Worker version/SHA.
2. List remote migrations:

   `pnpm exec wrangler d1 migrations list structurevidence-customer-cases --remote`

3. Query schema only, using D1 read-only SQL:

   - `PRAGMA table_list;`
   - `PRAGMA table_info('requests');`
   - `PRAGMA table_info('request_events');`
   - `SELECT name, type FROM sqlite_master WHERE type IN ('table','index','trigger') ORDER BY type,name;`

4. Quantify legacy note exposure without selecting note values:

   `SELECT event_type, COUNT(*) AS rows_with_note FROM request_events WHERE note IS NOT NULL AND length(trim(note)) > 0 GROUP BY event_type;`

5. If a schema artifact is required, use a no-data export and protect it as operational material:

   `pnpm exec wrangler d1 export structurevidence-customer-cases --remote --no-data --output <approved-path>`

References: [D1 SQL statements](https://developers.cloudflare.com/d1/sql-api/sql-statements/), [D1 import/export](https://developers.cloudflare.com/d1/best-practices/import-export-data/), [D1 migration commands](https://developers.cloudflare.com/workers/wrangler/commands/d1/).

Do not run `SELECT *`, export data, inspect note text, disable triggers, or copy production rows into a developer machine for this preflight.

## Legacy `request_events.note` boundary

The current branch prevents new public intake narrative from entering event notes. Existing notes require a separate, authorized disposition project:

1. classify with aggregate counts and narrow, authorized sampling only if counsel/operator approve;
2. decide retention, restriction and legal-hold rules before any content movement;
3. design a forward-only overlay or separately reviewed migration that can restrict admin projection without erasing append-only history;
4. test against synthetic fixtures representing ordinary, sensitive, restricted and legal-hold rows;
5. authorize any customer-row access, backup or transformation separately.

The remediation must not drop the append-only triggers or pretend that deleting the primary row removes Time Travel, logs, exports, mailbox copies or other historical replicas.

## Rehearsal and deployment order

1. Freeze the approved application SHA and migration checksums. Confirm 0001 and 0002 are applied and 0003 is pending.
2. In a clean non-production database, apply 0001–0003 in order and exercise synthetic old/new submissions, acknowledgement version/time, private-context separation, Access enforcement and old-client rejection.
3. Schedule a short maintenance/cut-over window because the new server rejects legacy, unversioned form payloads with HTTP 400. Purge or invalidate old form assets together with the Worker cut-over; no silent compatibility mode is allowed.
4. Before production migration, record an approved recovery point. Confirm actual Time Travel availability/age and perform a recovery drill against a non-production database. If operator policy requires an external backup, create it through the approved secure route; do not put it in Git.
5. Apply 0003 **before** deploying the new Worker. If application fails, stop and do not deploy the Worker.
6. Re-list migrations and inspect table/index/trigger names. Confirm no gap tables, canonical case state or historical event triggers changed.
7. Deploy the exact approved Worker build. Verify `/privacy/`, `/terms/`, form assets and the server-side notice version, then submit only an explicitly authorized synthetic smoke request.
8. Confirm the smoke request has one notice row, private context only in the restricted table/admin route, null submission event note, no narrative in response/logs, and no public endpoint exposure. Remove or mark the synthetic record only through an approved disposition process; do not bypass append-only controls.

## Failure handling and rollback limits

- Cloudflare documents that Wrangler captures a backup for migration application and rolls back the failed migration while retaining earlier successful migrations. This provider behavior must still be confirmed against the live account and recorded in the change ticket.
- A successful 0003 is operationally irreversible without data loss once new notice/private-context rows exist. Do not call the migration “reversible” merely because an empty synthetic database can be dropped.
- If 0003 fails: halt before Worker deployment, preserve diagnostics without customer content and restore/verify using the approved recovery procedure if required.
- If the Worker fails after 0003 succeeds: roll back the Worker artifact to the previous known-good version. Leave the additive tables in place; the previous Worker ignores them. Use a forward migration/fix for database defects rather than dropping tables.
- If privacy isolation fails: disable or roll back intake through an approved operational change, preserve Access protection and stop public submissions. Do not change case/evidence states as a repair mechanism.

## Permissions, evidence and maintenance record

Use least-privilege Cloudflare credentials with named human approval. Record the approver, operator, timestamps, pre/post migration list, Worker version, recovery point, non-sensitive schema verification and smoke result. Never record tokens or customer values in the release log.

## Historical-copy limits

A primary-record restriction or future deletion cannot promise immediate erasure from provider Time Travel, backups, exported archives, logs, email, payment/accounting records or third-party public blockchain history. Each system needs its own retention/legal-hold rule. Public wording must describe controlled requests and reasonable propagation, not guaranteed disappearance of every copy.
