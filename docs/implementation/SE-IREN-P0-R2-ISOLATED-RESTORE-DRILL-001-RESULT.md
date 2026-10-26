# SE-IREN-P0-R2-ISOLATED-RESTORE-DRILL-001 · Result

Authorization was confirmed, but the native-isolation preflight triggered the mandatory STOP gate before any database creation or restore.

```text
LOCKED_HEAD_SHA = 0b95ff5db2d299a4b6db6b1a3ce79f36da74d0ff
R2_AUTHORIZATION = YES
NATIVE_D1_INFO_READ = PASS
NATIVE_TIME_TRAVEL_BOOKMARK_READ = PASS
NATIVE_ISOLATED_RESTORE = UNSUPPORTED
ISOLATION_GATE = BLOCKED
R2_RESULT = STOPPED_BLOCKED_BEFORE_MUTATION
R2_RECOVERABILITY = UNKNOWN
R2_RPO = NOT_MEASURED_NO_ISOLATED_RESTORE
R2_RTO = NOT_MEASURED_NO_ISOLATED_RESTORE
READY_FOR_OWNER_PRODUCTION_RELEASE = NO
```

## UTC observation record

- Current Time Travel bookmark query: `2026-10-26T23:42:59.814Z` to `2026-10-26T23:43:12.388Z`.
- D1 metadata query: `2026-10-26T23:43:21.790Z` to `2026-10-26T23:43:32.330Z`.
- Source: `structurevidence-customer-cases` / `aee10591-536a-47af-8ee0-957551ba2360`.
- Source metadata observed read-only: APAC, read replication `auto`, 147,456 bytes, nine reported tables.
- The current bookmark was available. Its value was not printed, stored, or committed. Redacted evidence fingerprint: SHA-256 `d90ea6e1361082a6ad1cefe0ab5a0e96f23c4a420fd44abf495de3c57ba4d697`.

## Native capability and permission preflight

Authenticated `d1 info` and `d1 time-travel info` both succeeded. This confirms metadata-read and Time Travel bookmark-read capability for the named source. D1 create and restore-write permissions were intentionally not exercised because the isolation gate failed first.

Cloudflare's current [Time Travel documentation](https://developers.cloudflare.com/d1/reference/time-travel/) says that Time Travel is continuously available and restores to a point within the plan-dependent retention window. It also states that clone/fork to a new database is not yet supported and that the restore operation overwrites the selected database in place. The current [D1 Time Travel API](https://developers.cloudflare.com/api/resources/d1/subresources/database/subresources/time_travel/) exposes bookmark retrieval and restore on the same `database_id`; it exposes no source-to-new-target clone/fork operation.

The approved drill requires a new independent D1 target with no Worker binding or public route and prohibits an in-place production restore. Those conditions cannot both be satisfied by the current native Time Travel interface. Export/import was not substituted because it is not the authorized native isolated PITR path and would introduce a separate data-copy boundary.

## Mandatory stop outcome

- New recovery database: NOT CREATED.
- In-place restore: NOT INVOKED.
- Backup/export/import: NOT INVOKED.
- Copy to staging or local: NOT CREATED.
- Worker binding or route: NOT CREATED.
- Target aggregate, migration, schema, index, foreign-key and append-only-trigger comparisons: NOT RUN because no compliant target exists.
- Restore duration, measured RPO and measured RTO: NOT MEASURED.
- Target retention/cleanup: NOT APPLICABLE; no target or data copy was created.
- Account-specific 7-day versus 30-day retention tier: UNVERIFIED; no plan inference was made.

No production D1 write, migration `0003`, Worker deployment, production POST, PR merge or public Pilot occurred. No customer row, request ID, private identifier, Secret value, JWT, OTP, authentication header or raw bookmark is present in this report.

R2 remains `BLOCKED_UNSUPPORTED_NATIVE_ISOLATED_RESTORE`. Resumption requires a Cloudflare-supported source-to-new-private-target restore/clone operation, or a new owner authorization that explicitly defines a different isolated recovery mechanism and its data-handling controls.

## Validation

- R2 STOP and privacy guards: 2/2 PASS.
- Cloudflare landing/Worker suite: 60/60 PASS.
- Repository Python suite: 41 tests; 30 pass and 11 pre-existing failures; 0 new failures.
- Public record drift: PASS.
- Internal link audit: PASS; 0 orphan pages, 0 broken internal links, 0 cases without state and 0 evidence without parent.
- `NEW_REGRESSION_COUNT = 0`.
