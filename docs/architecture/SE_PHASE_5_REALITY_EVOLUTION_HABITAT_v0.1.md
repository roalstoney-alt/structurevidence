# Phase 5 Reality Evolution Habitat v0.1

StructEvidence studies how reality changes over time. It does not encode one industry as its core ontology.

## Canonical boundary

The canonical objects remain Subject, Evidence, State, ChangeEvent, Branch, Request, Challenge, and Outcome. `StructuralEventProjection` is derived at read time and creates no mutable duplicate store.

The projection contains Subject metadata, current State, Change history, supporting Evidence, counter-Evidence, open unknowns, Branches, authorized public Outcomes, snapshot proof, and RDL history. `as_of` is applied before projection so later-observed material cannot leak backward.

## Domain-neutral metadata

Subjects may add optional `domain`, `subdomain`, `object_type`, `spatial_scope`, and `change_mechanisms`. These fields are not required, so every historical Subject remains valid. Supported domains include technology, industry, geography, human geography, culture, environment, infrastructure, ecology, and institution.

## RDL policy

The frozen levels are `L0_SCAN`, `L0_VERIFY`, `L1_VERIFY`, and `L2_DEEP`. L0_SCAN always moves to verification. Further escalation requires a material potential change to State, unknowns, Branches, or Outcomes, or explicit human approval. Otherwise execution stops at `NO_STATE_CHANGE`.

Each run records query/source accounting, created evidence and unknown deltas, State before/after, decision change, runtime, observed costs, and output/snapshot hashes. Missing cost is `UNKNOWN`, never zero.

## Proof

`ProofProvider` defines the interface. `LocalHashProvider` implements P0 and `SnapshotChainProvider` implements the default P1 using canonical serialization, per-object hashing, and a Merkle-root-compatible calculation. P2 IPFS and P3 replication are reserved interfaces and are not activated.

Existing `state_hash`, `change_hash`, `content_hash`, and `chain_hash` fields are neither rewritten nor reinterpreted.

## Temporal API and surface

SE_API_v1 adds `/events`, event subresources, and `/atlas`. These are projections over canonical records. The public `/events` and `/atlas` surfaces remain text-first, evidence-first, unauthenticated, and explicit about unknowns and proof.
