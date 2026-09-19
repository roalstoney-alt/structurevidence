# Phase 2 Design — CML-PDRE-001

## Authorization

- Phase: `2` only
- Research level: `L0_REUSE`
- External research: prohibited
- Phase 3: not authorized
- Canonical evidence base: `technical-risk/cml-v1.1/pdre/CML-PDRE-001/`

## Decision boundary

Phase 2 asks whether repository-local evidence can reconstruct a decision-useful baseline. It does not decide whether 800VDC will succeed, change CML readiness, verify missing evidence, or perform commercial research.

## Retrieval order

The execution inspected the case index, canonical PDRE record, dependency transfer, timelines, and case metadata. It then normalized only decision-relevant references. No source was refreshed and no repository-wide evidence corpus was scanned.

## Outputs

Machine-readable outputs live under `rdl/research/records/CML-PDRE-001-PHASE-2/`. They reference canonical CML evidence and do not copy full source content or create a parallel evidence store.

## Semantic controls

- Event time and knowledge time remain distinct.
- Missing evidence remains `UNKNOWN`, not `UNSUPPORTED`.
- Counter-evidence remains separately identified.
- Readiness remains CML authority: PDRE-001A is `R3`; PDRE-001B is `NOT_ASSIGNED`.
- Narrative evidence does not establish qualification or deployment.
- Future L1 items are candidates for human review only.

## Schema observation

The schema-required `minimum_missing_evidence` field was populated with the repository mapping needed to complete the methodological decision. This real case suggests a future schema review could consider allowing an empty array at research start. Phase 2 did not change the schema.
