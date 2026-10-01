# StructureEvidence

**Time-indexed evidence → Decision memory → Workflow → Outcomes**

StructEvidence records how public evidence changes the state of real-world technical and industrial claims. It turns uncertain evidence into scoped, traceable, revisable decision objects.

The underlying source facts may be public. The compounding asset is the structured history of what was accepted, rejected, contradicted, unknown, decision-relevant, frozen, reopened, and later observed in the real world.

Canonical records: https://structurevidence.org

This repository is the verification layer for reproduction, inspection, challenge, citation, and contribution. The website remains the canonical truth source. Public records preserve claims, evidence, counter-evidence, unknowns, search boundaries, state transitions, and verification history.

## Scholarly Record

Current method paper:

**From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States**

Version DOI: https://doi.org/10.5281/zenodo.23033588

Concept DOI (all versions): https://doi.org/10.5281/zenodo.23033587

Zenodo: https://zenodo.org/records/23033588

The Version DOI identifies this exact v0.1 publication. The Concept DOI identifies the paper family and resolves to the latest version.

Protocol: `QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1`

Implementation baseline: `94ee5dc8670b8132979846c815b400f8cef17ab1`

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

## Public verification

- [Case discovery index](https://structurevidence.org/cases/)
- [Material change record](https://structurevidence.org/changes/)
- [Contribution protocol](CONTRIBUTING.md)
- [Citation metadata](CITATION.cff)

```sh
python3 scripts/export_public_records.py
python3 scripts/check_public_record_drift.py
python3 scripts/audit_internal_links.py
```
