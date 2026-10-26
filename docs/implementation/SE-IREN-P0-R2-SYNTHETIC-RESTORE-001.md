# SE-IREN-P0-R2-SYNTHETIC-RESTORE-001 · Execution specification and current checkpoint
Date: 2026-10-27; authorization: user explicitly approved two NEW isolated Cloudflare D1 databases containing synthetic data only, SQL export/import and measurements. No production data export/read/write, production worker changes, migration 0003 against production, production POST, PR merge, or public pilot.
Verified PR #54 pre-run HEAD: 745c9a1e56ad5e3c3dc1c8ea4504fd66163c8aeb; base main 56f8e345ddfc697855c8eb9492dc0b49d24c6fcc.
At authoring time, this assistant has GitHub repository actions but NO Cloudflare management connector or authenticated Wrangler terminal. Therefore real Cloudflare source/target creation, export/import and RTO/RPO were NOT PERFORMED. Only this spec was committed; do not label execution PASS.

## Source-backed API constraints
See https://developers.cloudflare.com/d1/best-practices/import-export-data/ and https://developers.cloudflare.com/d1/wrangler-commands/.
Cloudflare supports `wrangler d1 export <NAME> --remote --output=...` and `wrangler d1 execute <NAME> --remote --file=...` into another database. Imports may require removal of explicit BEGIN/COMMIT and reserved _cf_KV DDL; FK statement/table ordering and triggers must be verified, not presumed. SQL export temporarily blocks requests to exported source. Use brand-new synthetic source not live production.

## Cloudflare operator implementation (Codex action)
0. Re-lock current PR HEAD; ensure no more than intended docs changes. Verify Cloudflare account and D1 privilege, available DB quota, current Wrangler syntax with `wrangler d1 --help`. Refuse if named source ID equals production aee10591-536a-47af-8ee0-957551ba2360 or staging 65dc6680-0832-401d-8772-6a082b68673c. Never copy data from either.
1. Choose time-suffixed unique source and destination names `se-iren-r2-synthetic-source-YYYYMMDD-<nonce>`, `se-iren-r2-synthetic-target-YYYYMMDD-<nonce>`. Use authenticated Wrangler `d1 create` for each; do not attach either to any Worker or publish routes. Inspect Cloudflare account isolation, permissions, target/production IDs and retain only aliases/hashed IDs in public repo reports. If resources already exist with names, STOP; do not reuse.
2. Apply production-equivalent migrations 0001,0002,0003 to synthetic SOURCE DB only, using explicit `--remote` and a dedicated safe `wrangler` config that binds only source/target aliases, never prod. Verify the migration commands' exact options in installed Wrangler. Do NOT use production `wrangler.jsonc` binding or any default database selection. Test schema metadata, FK, five core tables and four event/consent UPDATE+DELETE guards.
3. Seed synthetic records directly into source using stable IDs prefixed `R2_SYNTHETIC_` and `example.invalid` email domain, but NEVER use real personal information or production IDs. Exercise at least: 3 synthetic customers, 3 synthetic requests, 5 synthetic events, 3 consent receipts, 3 idempotency mappings. Existing append-only event triggers may require ordering; seed with SQL INSERT only. Ensure referential integrity and known deterministic row-level fixture hashes calculated from synthetic values only.
4. Pre-export: record UTC timestamp, source schema fingerprints (tables, columns, index names, FK metadata, trigger names), five table counts, `PRAGMA foreign_key_check`; record hash of synthetic fixture manifest. Check absence of all Worker bindings and routes.
5. Export SOURCE to a restricted ephemeral SQL file using Wrangler D1 remote export. The SQL contains SYNTHETIC data only, so temporary file is allowable but must not include auth credentials. Exclude file from Git, logs and uploads. Capture bytes SHA-256, size, start/end UTC, latency and observed source unavailability when possible. Do not claim production downtime based on this synthetic sample.
6. Import into independent TARGET using `wrangler d1 execute <TARGET> --remote --file=<ephemeral_sql_path>` or documented Cloudflare import workflow. Never apply migrations before importing full-schema SQL to avoid table-already-exists errors. If import error arises, preserve private diagnostic and fail; only transform documented BEGIN/COMMIT or _cf_KV syntax in a controlled copy with before/after hashes and revalidate semantic schema+row equality. Distinguish unmodified round-trip PASS from transformed-round-trip CONDITIONAL.
7. Verify TARGET five user tables, row counts, sorted synthetic fixture checksum (only synthetic data), FK zero violations, expected indexes, 4 append-only guards, consent version, private default/authorization, and migration ledger behavior. Test UPDATE and DELETE against restored synthetic event and consent receipt and require constraint errors without row changes. Verify original synthetic SOURCE unaffected after export; independent target database ID. Any extra D1 internal system tables must be identified instead of asserted identical to user schema.
8. Measure: `RTO_OBSERVED` = time from simulated outage marker to target integrity-ready, including export/import? Report separate `export_duration`, `import_duration`, `validation_duration`, `total_drill_duration`, and whether hypothetical backup preexists. `RPO_SYNTHETIC` = known number/time of fixture writes between simulated backup cutoff and failure; if no added post-snapshot write, label `ZERO_IN_STATIC_FIXTURE_ONLY`, not production RPO. Never extrapolate directly to production workload.
9. Retention: target no Worker routes and no PII; either keep both isolated as explicitly approved short-lived test artifacts with an expiry date and owner cleanup request, or delete only synthetic databases under declared test retention policy and record actual Cloudflare deletion confirmation. Do not remove production/staging resources. No unverified deletion claim.
10. Append-only redacted result into PR #54, including exact commit SHA (post-write), IDs in non-sensitive form, provenance, SQL export/import command versions, source/target separate, measured times, table counts, triggers, FK, checksum, limitations (synthetic-only cannot verify production data restore), and `NEW_REGRESSION_COUNT`. Never include Cloudflare tokens, secret, real customer rows or transient SQL dump. Update human privacy gate unchanged.

## Stop conditions
Any database name/ID ambiguous or production/staging involved; no isolated source/target; SQL export not working; schema roundtrip loses constraint, trigger or migrations; target FK errors; unapproved third-party transfer; controls need credential bypass; actual command might apply 0003 to production; inability to account for ephemeral SQL lifetime; Cloudflare read/write tools missing. On stop, report `STOPPED_BEFORE_MUTATION` if no action taken, otherwise precisely list synthetic-only operations.

## Current checkpoint (this assistant interaction)
R2_SYNTHETIC_AUTHORIZED=YES
GITHUB_BASE_VERIFIED=YES
CLOUDFLARE_MANAGEMENT_CONNECTOR=UNAVAILABLE
SYNTHETIC_SOURCE_CREATED=NO
SYNTHETIC_TARGET_CREATED=NO
REMOTE_SQL_EXPORT=NOT_RUN
REMOTE_SQL_IMPORT=NOT_RUN
SCHEMA_FK_INDEX_TRIGGER_ROUNDTRIP=NOT_TESTED
RECOVERY_DURATION=NOT_MEASURED
PRODUCTION_CUSTOMER_DATA_ACCESSED=NO
PRODUCTION_D1_MUTATED=NO
PRODUCTION_MIGRATION_0003=NOT_APPLIED
PRODUCTION_WORKER_DEPLOYED=NO
PRODUCTION_POST=0
PR54_MERGED=NO
PUBLIC_PILOT=NO
