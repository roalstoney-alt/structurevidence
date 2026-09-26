# StructEvidence Temporal State Protocol v0.1

Status: frozen for SE-FRR-001 Phase 1.

The protocol represents a subject through evidence-bounded, immutable observations:

`Subject → Evidence → State → Change → Branch → Request → Human Action → Outcome`

## Time semantics

- `published_at`: the source's claimed publication time; it may be null.
- `observed_at`: when StructEvidence acquired or observed the information.
- `recorded_at`: when the protocol object entered StructEvidence.
- `effective_at`: an independently stated effective time; it may be null.

These fields are not interchangeable. A future effective time and a late observation never rewrite an earlier State.

## State rule

Each State describes what was supportable at one observation boundary. Canonical States are append-only. New information creates new Evidence and a new State. A material transition also creates a Change Event linking both immutable State hashes. `append_state` rejects an existing ID, a non-tail predecessor, or an invalid state/chain hash.

The Phase 1 vocabulary is frozen to the eight values in `state.schema.json`. Confidence is expressed only as supported, unsupported, and unknown boundaries; the protocol has no numeric confidence or branch probability.

Rejected, counter, unresolved, and superseded Evidence remains present. Supersession records displacement, never deletion.

## Outcome rule

An Outcome records action taken using a State. It cannot mutate that State. A supported or verified Outcome may enter a later review path as new Evidence, after which a later State may be appended.

## Version freeze

`SE_TEMPORAL_PROTOCOL`, Subject, Evidence, State, Change, Branch, Request, Challenge, and Outcome are all frozen at v0.1. Incompatible changes require a new schema version and migration logic.
