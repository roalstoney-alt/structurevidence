# StructureEvidence

**Time-indexed evidence → Decision memory → Workflow → Outcomes**

StructureEvidence turns uncertain industrial and technical evidence into scoped, traceable, revisable decision objects.

The underlying source facts may be public. The compounding asset is the structured history of what was accepted, rejected, contradicted, unknown, decision-relevant, frozen, reopened, and later observed in the real world.

Official website: https://structurevidence.org

## Core layers

- **Evidence Core** — provenance and shared record envelope.
- **CML** — structural interpretation, path-dependency release, migration readiness, and transferred dependencies.
- **RDL** — bounded research authorization, allocation, telemetry, and stop rules.
- **Decision Memory** — cross-domain, append-only history linking evidence states, unknowns, decisions, workflow actions, reopen triggers, and outcomes.
- **Public Evidence Cases** — human-readable snapshots that expose the method without claiming public facts as proprietary data.

## Decision Memory v0.1

- [Architecture](docs/architecture/DECISION_MEMORY_v0.1.md)
- [Schema](evidence/decision-memory/schema/decision-memory-record.schema.json)
- [Sodium-ion BESS frozen state](cases/sodium-ion-bess/state-v0.1.json)
- [Sodium-ion BESS Decision Memory](cases/sodium-ion-bess/decision-memory-v0.1.json)

Five time semantics are preserved where available:

`event_at → published_at → first_observed_at → known_at → frozen_at`

Existing dual-clock records remain valid. Missing historical observation timestamps stay unknown rather than being reconstructed with hindsight.

## Product boundary

StructureEvidence separates:

`FACT ≠ CLAIM ≠ EVIDENCE ≠ DECISION ≠ OUTCOME`

It does not convert source volume into truth, single deployments into industry adoption, or public evidence maps into buyer-specific recommendations without decision context.

This project does not provide investment recommendations or automated accusations.
