# StructureEvidence Decision Memory v0.1

## Purpose

StructureEvidence is moving from a collection of evidence reports toward a time-indexed decision-memory layer.

The compounding product loop is:

```
PUBLIC / CUSTOMER EVIDENCE
        ↓
NORMALIZED EVIDENCE STATE
        ↓
TIME-INDEXED DECISION MEMORY
        ↓
EMBEDDED VERIFICATION / PROCUREMENT / DILIGENCE WORKFLOW
        ↓
ACTION
        ↓
REAL-WORLD OUTCOME
        ↓
APPEND-ONLY OUTCOME LINKAGE
```

Public source facts are not proprietary. The proprietary layer is the accumulated normalization and history of what was accepted, rejected, contradicted, unknown, decision-relevant, frozen, reopened, and later observed in the real world.

## System boundaries

Existing components remain authoritative within their domains:

- Evidence Core: shared provenance and record envelope.
- CML: structural interpretation and migration-readiness logic.
- RDL: bounded research authorization, allocation, telemetry, and stopping.
- Public cases: human-readable evidence-state snapshots.
- Decision Memory: cross-domain historical record linking evidence states, unknowns, decisions, workflow actions, and outcomes over time.

Decision Memory does not replace CML or RDL. It references them.

## Non-negotiable invariants

1. Scope precedes conclusion.
2. Evidence state and decision state are separate objects.
3. Counter-evidence is first-class.
4. UNKNOWN is a valid result.
5. Public facts are not claimed as proprietary assets.
6. Source count does not imply source independence.
7. Single-instance evidence does not imply market adoption.
8. Historical snapshots are append-only.
9. Later outcomes never rewrite what was knowable at an earlier cutoff.
10. Every frozen state defines reopen conditions.
11. Research may stop when the decision-sensitive unknown is resolved.
12. Scores must not erase evidence structure.

## Five time semantics

New Decision Memory records use five distinct clocks:

- `event_at`: when the underlying event occurred.
- `published_at`: when the source made the event or claim public.
- `first_observed_at`: when StructureEvidence first encountered the source, if captured.
- `known_at`: when the source was accepted into the bounded evidence state.
- `frozen_at`: when the corresponding state or decision snapshot was frozen.

Backward compatibility:

- Evidence Core `effective_at` maps to the relevant event or snapshot effective time.
- Evidence Core `known_at` remains authoritative for accepted knowledge time.
- Existing dual-clock records remain valid.
- Missing historical `first_observed_at` stays `null`; it must not be reconstructed from hindsight.

The sodium-ion case demonstrates why this matters: the 60 GWh agreement event occurred on 2026-04-27, HyperStrong published on 2026-04-29, CATL published on 2026-05-06, and StructureEvidence accepted the evidence into the v0.1 case at the 2026-09-24 cutoff.

## Evidence state vs decision state

Evidence state answers: what does the accepted evidence establish within this scope?

Decision state answers: given a specific decision context, what action state follows?

A public evidence case may legitimately have `decision_state.status = CONTEXT_REQUIRED`. This prevents a market evidence map from silently becoming procurement advice.

## Unknown object

An unknown is not a free-text remainder. It carries:

- question
- why it is unknown
- decision sensitivity
- affected state(s)
- minimum resolving evidence
- resolution path
- candidate research level
- stop condition

This makes unknowns allocatable research capital rather than a generic request for more search.

## Reopen triggers

Every frozen state declares the minimum future evidence that would reopen it. This turns passive reports into monitorable workflow objects.

## Outcome linkage

Outcomes are appended to the original frozen decision/state and never used to overwrite history.

Target graph:

```
SOURCE
  ↓
EVIDENCE OBSERVATION
  ↓
CLAIM / STATE
  ↓
UNKNOWN / DEPENDENCY
  ↓
DECISION
  ↓
AUTHORIZED ACTION
  ↓
OUTCOME
  ↓
REVISION / REOPEN EVENT
```

## Sodium-ion BESS migration

The frozen file `cases/sodium-ion-bess/state-v0.1.json` remains unchanged.

The sidecar `cases/sodium-ion-bess/decision-memory-v0.1.json` adds evidence-state/decision-state separation, five-clock temporal semantics, source publication lag, decision-sensitive unknowns, reopen triggers, workflow bindings, outcome references, and the public-source/proprietary-derived-data boundary.

Future snapshots should append new Decision Memory revisions instead of overwriting v0.1.
