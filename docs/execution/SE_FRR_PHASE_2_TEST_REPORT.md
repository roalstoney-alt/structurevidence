# SE-FRR-001 Phase 2 Test Report

Date: 2026-09-26

## Results

| Suite | Result |
|---|---|
| Frozen historical Python baseline | 255/258 pass; 2 failures + 1 error exactly match 3 frozen exceptions |
| Phase 1 protocol tests | 26/26 pass |
| Phase 2 repository + contract tests | 8/8 pass |
| Worker total | 36/36 pass |
| Phase 2 Worker/API tests within total | 23/23 pass |
| Unified SE-FRR validator | PASS — 15 objects, zero errors |
| State-chain verifier | PASS — 1 chain, zero broken links/hash mismatches |
| OpenAPI contract validator | PASS — 21/21 operations |
| Wrangler | PASS — dry-run only, no deployment |

Phase 2 therefore has 31/31 new tests passing: 23 API/Worker cases, 5 materializer cases, and 3 contract cases.

## Required behavior covered

Tests exercise Subject list/lookup, current State, ordered State history, Change feed/filtering, Evidence separation, probability-free Branches, unknown IDs, traversal-shaped IDs, temporal `as_of`, retrospective leakage prevention, ETag/304, Request submission/status, Challenge and Outcome non-mutation, sequential idempotency, private-data absence, unexpected fields, malformed JSON, oversized payloads, wrong Access audience, proposal validation/approval, clean-tree enforcement, previous-tail verification, full chain validation, no overwrite, and OpenAPI operation/status/input allowlists.

## Frozen baseline signatures

- `ValueError: Phase A history entry`.
- Phase B `OV-B01_BASELINE_INTEGRITY`: 12 pass, 1 fail, 3 not evaluated.
- Phase B-R1 `OV-R101_ACCEPTED_WAVE1_BASELINE`: 7 pass, 1 fail.

No new unexplained failure appeared. The pre-existing `jsonschema.RefResolver` warning remains non-failing deferred debt.

Final Wrangler dry-run bundle: 144.12 KiB / gzip 36.14 KiB.
