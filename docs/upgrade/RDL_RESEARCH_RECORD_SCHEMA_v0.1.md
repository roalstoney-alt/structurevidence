# RDL Research Record Schema v0.1

## Canonical identity

`schema_version = RDL_RESEARCH_RECORD_v0.1`

Machine-readable schema:

`rdl/research/schema/research-record.schema.json`

The document has two closed top-level fields:

```text
core             existing StructEvidence Evidence Core
research_record  RDL research-process payload
```

## Required fields

The payload implements all authorized minimum fields: research/case/PDRE/customer identity, level/class/initiator, start/completion time, decision target, question, before/after references, knowns/unknowns, minimum missing evidence, hypothesis/readiness/decision before and after, decision delta, actions, query/source/evidence references, unknown resolution, reusable assets, stop reason, review requirement, telemetry, and notes.

Additional required structures provide:

- external authorization state for L2/L3 representation;
- search-memory lookup keys;
- boundary references to existing authoritative systems;
- explicit `CML_REFERENCE_ONLY` structural authority;
- append/supersession revision history.

## Reference-first design

Evidence, claims, sources, state, manifests, authorizations, and outcomes are represented by stable references. The schema does not define an evidence payload or reproduce CML/timeline/GDR objects.

## Before/after semantics

`before_state_ref` and `after_state_ref` identify authoritative snapshots. The record additionally captures the research-relevant knowns, unknowns, hypothesis, readiness, and decision to make research rounds comparable. RDL records these values; it does not become the CML or ECN authority.

If `decision_changed = true`, the validator requires:

- different non-placeholder before/after decisions;
- a non-empty reason.

If false, before and after decisions must remain equal.

## Failed research

`new_evidence_refs` may be empty. `DUPLICATE_ONLY` requires at least one duplicate reference and zero new references. Public-data-insufficient, unavailable-source, exhausted-search, contradicted-evidence, wrong-hypothesis, and failed-commercial-relevance results remain valid records.

## Search-memory foundation

The schema requires lookup arrays for claims, hypotheses, entities, components, standards and migration paths. Combined with the decision target, question, case/PDRE identity, minimum missing evidence and stop reason, these fields enable later deterministic indexing without Phase 1 semantic search.

## Immutability and legacy policy

Each revision must preserve the original. Historical artifacts without this record use `LEGACY / PRE-RDL-RESEARCH-RECORD` semantics: canonical research-of-research data is unavailable, not evidence that no research occurred.

## Prohibited fields and behavior

The closed schema and semantic validator reject private raw prompts/credentials, parallel structural authority, opaque confidence/research-quality/MEV scores, overlapping new/duplicate evidence roles, unapproved L2/L3 representation, and UNKNOWN telemetry encoded as zero.
