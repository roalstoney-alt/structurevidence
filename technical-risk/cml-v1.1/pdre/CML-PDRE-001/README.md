# CML-PDRE-001

`800VDC / SST AI DATA CENTER POWER ARCHITECTURE`

This directory is the private discovery container for the first CML v1.1 PDRE tracking case. Initialization does not establish that a PDRE occurred, does not establish any technical or commercial fact, and does not assign migration readiness.

## Status

- Research: `DISCOVERY_ACTIVE`
- Publication: `PRIVATE_DRAFT`
- Approved evidence packets: `0`
- Canonical PDRE record: not instantiated pending approved evidence

## Research units

The case must preserve two distinct units of analysis:

| Unit | Old-path scope | New-path scope |
| --- | --- | --- |
| `PDRE-001A` | 54V in-rack distribution | 800VDC sidecar / power rack |
| `PDRE-001B` | Traditional facility AC conversion chain | Centralized 800VDC / SST |

These descriptions are user-provided research scope, not evidence.

## Files

- `CASE.json` — case identity, scope, schema bindings, research-unit separation, and unassessed tracking state.
- `timeline.jsonl` — append-only case timeline; currently contains only the administrative initialization event.
- `evidence-index.jsonl` — append-only evidence intake index; currently records that no approved packet exists.
- `state-history.jsonl` — append-only research and publication state history.
- `dependency-transfer.json` — category matrix for dependency release and dependency transfer, initialized as unknown.

## Evidence and readiness rules

The case reuses the accepted CML v1.1 schemas referenced by `CASE.json`; it does not create a parallel evidence model. The accepted canonical PDRE schema requires a migration-readiness code. Because no approved evidence packet exists, creating a populated `PDRE_RECORD` would force an unsupported assignment. The canonical record is therefore deferred, and both research units retain `NOT_ASSIGNED` with a null code.

No external fact, URL, evidence reference, readiness level, adoption-friction conclusion, structural-exposure conclusion, beneficiary conclusion, economic conclusion, real-world response, or market-validation outcome may be added without an approved evidence packet. Unknown values must not be converted into positive or negative findings.
