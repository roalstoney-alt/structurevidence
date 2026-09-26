# SE-FRR-001 Phase 1 Test Report

Date: 2026-09-26

## Phase 1 suite

Command: `python3 -m unittest discover -s tests/se_frr -p 'test_*.py' -v`

Result: **26/26 PASS**.

Coverage includes all eight schemas, invalid-object rejection, four-time semantics, independent effective time, deterministic serialization, Evidence and State hashes, mutation detection, immutable append, predecessor enforcement, Change linkage, retained rejected/counter/superseded Evidence, two simultaneous branches without probabilities, Outcome-to-later-Evidence conversion, public/private projection, reference failures, and two existing-system adapters.

## Protocol acceptance commands

| Command | Result |
|---|---|
| `python3 scripts/validate_se_frr.py` | PASS — 15 objects; 0 schema/reference/hash/chain/privacy errors |
| `python3 scripts/verify_se_state_chain.py` | PASS — 1 subject; 2 States; 1 valid chain; 0 broken links/mismatches |
| `python3 scripts/export_se_public.py --output /tmp/se-frr-public.json` | PASS — 12 public objects; 0 private Requests exported |

## Historical baseline

Command: `python3 -m unittest discover -s scripts -p 'test_*.py'`

Result: **255/258 PASS; 2 failures and 1 error**. All three signatures exactly match `SE_FRR_KNOWN_BASELINE_EXCEPTIONS_v0.1`; no Phase 1 or unexplained failure appeared.

- B-001: `ValueError: Phase A history entry`.
- B-002: Phase B `OV-B01_BASELINE_INTEGRITY`, 12 pass / 1 fail / 3 not evaluated.
- B-003: Phase B-R1 `OV-R101_ACCEPTED_WAVE1_BASELINE`, 7 pass / 1 fail.

The existing `jsonschema.RefResolver` deprecation warning remains non-failing technical debt.

## Existing application checks

- Cloudflare Worker: **13/13 PASS**.
- Wrangler: **PASS**, `deploy --dry-run`; 116.95 KiB / gzip 29.84 KiB; no deployment.

`NEW_UNEXPLAINED_FAILURES = 0`.
