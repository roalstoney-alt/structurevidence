# SE-IREN-P0-R2-SYNTHETIC-RESTORE-001 · Result

The synthetic-only Cloudflare D1 export/import drill completed successfully. This result does not establish production recoverability or production RPO/RTO.

```text
LOCKED_HEAD_SHA = dfa72a5935e9c5cb6e1cb06a2fd4042c5ad7ac55
R2_SYNTHETIC_RESULT = PASS_SYNTHETIC_ONLY_UNMODIFIED_ROUNDTRIP
SYNTHETIC_FIXTURE_INTEGRITY = PASS
SYNTHETIC_SCHEMA_CONSTRAINT_INTEGRITY = PASS
SYNTHETIC_RPO = ZERO_IN_STATIC_FIXTURE_ONLY
SYNTHETIC_RTO_OBSERVED_SECONDS = 231.039
PRODUCTION_RPO_RTO_INFERRED = NO
PRODUCTION_RECOVERABILITY = UNKNOWN
READY_FOR_OWNER_PRODUCTION_RELEASE = NO
```

## Isolated resources

Two new APAC D1 databases were created with unique names and distinct IDs. Neither ID matched production or staging. Only ID SHA-256 fingerprints are recorded:

- Source `se-iren-r2-synthetic-source-20261027-a7c9`: `03634f5dacb51fe920caac070d38cb2b70f55a82d76c91b2806690fd8a2cb7ea`.
- Target `se-iren-r2-synthetic-target-20261027-a7c9`: `f7559ee22237c09d8c8a8b9a306f38e2d662c1d351ba54753d9eacefc122e24c`.

Database creation did not update any repository or production Wrangler configuration. A dedicated `/tmp` config contained only the two synthetic database IDs. No Worker with the synthetic config name existed, no deployment was made, and no route was created.

## Synthetic source

Only the synthetic source received migrations `0001_customer_intake.sql`, `0002_open_evidence_gaps.sql` and `0003_intake_hardening.sql`. The deterministic fixture used only `R2_SYNTHETIC_` IDs and `example.invalid` addresses:

| Table | Count |
|---|---:|
| customers | 3 |
| requests | 3 |
| request_events | 5 |
| request_consent_receipts | 3 |
| request_idempotency | 3 |

No Gap records were seeded. Consent version/acceptance/actor, 64-character idempotency hashes, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, null owner, indexes, four required foreign-key relationships and zero FK violations were verified.

## Export/import and integrity

- Export: `2026-10-27T00:01:18.006Z`–`00:01:35.059Z`; 17.053 seconds.
- Exported SQL: 13,825 bytes; SHA-256 `d9f39c97d711972b079f12de95989f0e709ae82e853a9e6f6cf7022c367e94b0`.
- Import: `2026-10-27T00:02:14.847Z`–`00:02:27.608Z`; 12.761 seconds.
- The target was empty and was not pre-migrated. The exported SQL was imported without transformation.
- Initial semantic validation: 21.771 seconds.
- Four target append-only UPDATE/DELETE rejection tests: 42.499 seconds; all four rejected with no row mutation.
- Final integrity-ready time: `2026-10-27T00:05:09.045Z`.

Source and target fixture hash:

`3f2c7c299bb7037be4d686dc95bb97e006804cd89c66a15814268e5c09b95696`

Source and target schema/column/index/FK/migration metadata hash:

`03b84ba7f1dfb20fb846018370e67d23046496e95ba3c98bd48c063b42a4be38`

Both pairs matched. All five intake tables, required indexes, three migration ledger entries, Consent, Idempotency and these four append-only triggers survived the round-trip:

- `request_events_no_update`
- `request_events_no_delete`
- `request_consent_receipts_no_update`
- `request_consent_receipts_no_delete`

The additional `0002` Gap tables and their triggers also survived. `_cf_KV` was identified as a D1 internal table and was not present in the exported SQL.

## Synthetic RPO/RTO boundary

`RTO_SYNTHETIC_OBSERVED = 231.039 seconds`, measured from the synthetic export start marker to the final integrity-ready check. It includes export, import, semantic validation and append-only guard validation, as well as orchestration latency.

`RPO_SYNTHETIC = ZERO_IN_STATIC_FIXTURE_ONLY`: no synthetic fixture writes occurred after the export cutoff marker. Neither measurement is extrapolated to production workload, production volume, production outage behavior or production recoverability.

## Retention and cleanup

Retention policy was `DELETE_AFTER_VALIDATION`.

- Target deleted: `2026-10-27T00:05:35.705Z`–`00:05:47.783Z`.
- Source deleted: `2026-10-27T00:05:47.783Z`–`00:05:59.864Z`.
- Absence of both synthetic databases and continued presence of production/staging were confirmed at `2026-10-27T00:06:57.820Z`.
- Temporary SQL, seed and dedicated Wrangler config were deleted from `/tmp` and were never added to Git.
- Total drill duration through cleanup confirmation: 667.055 seconds.

No production customer row was read or exported. Production D1, Worker, migration state and HTTP traffic were untouched; production POST count remains zero. PR #54 remains Draft and unmerged, and no public Pilot was started.

## Validation

- Synthetic restore report guards: 2/2 PASS.
- Cloudflare landing/Worker suite: 62/62 PASS.
- Repository Python suite: 41 tests; 30 pass and 11 pre-existing failures; 0 new failures.
- Public record drift: PASS.
- Internal link audit: PASS; 0 orphan pages, 0 broken links, 0 cases without state and 0 evidence without parent.
- `NEW_REGRESSION_COUNT = 0`.
