# CML-PDRE-001

`800VDC / SST AI DATA CENTER POWER ARCHITECTURE`

This directory is the private discovery container for the first CML v1.1 PDRE tracking case. Approved evidence packet `CML-PDRE-001-EVP-001` has been ingested for `PDRE-001A` only. It supports candidate PDRE status and the specifically authorized readiness state; it does not establish qualification, deployment, commercial migration, or a result for `PDRE-001B`.

## Status

- Research: `DISCOVERY_ACTIVE`
- Publication: `PRIVATE_DRAFT`
- Approved evidence packets: `1`
- `PDRE-001A`: `CANDIDATE`, `R3 — SAMPLE_BENCH_TESTED`, `TECHNICALLY_CREDIBLE`
- `PDRE-001B`: `ACTIVE_SUBHYPOTHESIS`, readiness `NOT_ASSIGNED`
- Canonical PDRE record: `pdre-record.json`, private draft, scoped to `PDRE-001A`

## Research units

The case must preserve two distinct units of analysis:

| Unit | Old-path scope | New-path scope |
| --- | --- | --- |
| `PDRE-001A` | 54V in-rack distribution | 800VDC sidecar / power rack |
| `PDRE-001B` | Traditional facility AC conversion chain | Centralized 800VDC / SST |

These descriptions are user-provided research scope, not evidence.

## Files

- `CASE.json` — case identity, scope, schema bindings, research-unit separation, and unassessed tracking state.
- `timeline.jsonl` — append-only case timeline containing the preserved initialization event, source-time observations, and packet-ingestion event.
- `evidence-index.jsonl` — append-only evidence intake index containing the preserved initialization control and seven approved packet records.
- `state-history.jsonl` — append-only research and publication state history.
- `dependency-transfer.json` — category matrix partially assessed for `PDRE-001A`; all `PDRE-001B` entries remain unknown.
- `pdre-record.json` — canonical CML v1.1 PDRE record for `PDRE-001A`, instantiated from the approved packet.

## Evidence and readiness rules

The case reuses the accepted CML v1.1 schemas referenced by `CASE.json`; it does not create a parallel evidence model. `PDRE-001A` now has an approved packet and the authorized readiness assignment. `PDRE-001B` remains outside that assignment and retains `NOT_ASSIGNED` with a null code.

No additional fact, URL, evidence reference, readiness level, adoption-friction conclusion, structural-exposure conclusion, beneficiary conclusion, economic conclusion, real-world response, or market-validation outcome may be added without an approved evidence packet. Vendor performance and forward-looking claims remain explicitly source-attributed and are not independently validated facts. Unknown values must not be converted into positive or negative findings.
