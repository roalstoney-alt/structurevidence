# Phase 1 Design — RDL Research Governance

## Objective

Phase 1 adds one canonical envelope for observing research. It records why bounded research occurred, its before/after state, work, raw cost telemetry, decision delta, reusable output, and stop condition. It surrounds existing artifacts by reference.

```text
RESEARCH PROCESS
       |
       v
RDL_RESEARCH_RECORD_v0.1
       |
       +-- WHY
       +-- BEFORE
       +-- WORK
       +-- COST
       +-- AFTER
       +-- DECISION DELTA
       +-- REUSABLE OUTPUT
       +-- STOP
```

## Implemented paths

- Schema: `rdl/research/schema/research-record.schema.json`
- Template: `rdl/research/templates/research-record.template.json`
- Validator: `rdl/research/validation/validator.py`
- Vocabularies: `rdl/research/vocabulary/`
- Synthetic fixtures: `rdl/research/fixtures/`
- Canonical Phase 1 record: `rdl/research/records/RDL-METHODOLOGY-PHASE-1-2026-09-19.json`
- Module manifest: `rdl/research/RDL_RESEARCH_RECORD_MANIFEST.json`
- Tests: `scripts/test_rdl_research_record.py`

## Reuse architecture

The top-level `core` field references the existing StructEvidence Evidence Core schema. The research payload stores stable references to evidence, CML state, timelines, RTP-style manifests, GDR-SE authorization records, and outcomes. It does not reproduce their contents or authority.

No evidence store, timeline system, CML state store, authorization system, database, or provenance architecture was created.

## Canonical record sections

| Section | Purpose |
| --- | --- |
| Identity/scope | Research, case, PDRE and nullable customer-case identity |
| Governance | L0–L3, research class, initiator and external authorization state |
| Decision target | Decision to change, research question and minimum missing evidence |
| Before/after | Knowns, unknowns, hypothesis, readiness and decision references/state |
| Actions | Bounded work items, level, external-research flag, inputs, outputs and limitations |
| Evidence delta | Checked/used/rejected sources and new/counter/duplicate evidence references |
| Telemetry | Raw observed, estimated or unknown call/token/cost/time measurements |
| Lookup keys | Claim, hypothesis, entity, component, standard and migration-path references |
| Boundaries | References to existing Evidence Core, CML, timeline, RTP, GDR and outcomes |
| Stop/revision | Normalized stop reason, human-review flag and append/supersession history |

## Authorization behavior

L0 and L1 may be represented with `NOT_REQUIRED`. L2 and L3 cannot use `NOT_REQUIRED`; they must be pending, authorized, or denied by an external authority. An authorized L2/L3 record requires an authorization reference. The RDL validator records the state but never grants authorization.

## Immutability

Research records use Evidence Core correction and supersession fields plus a required revision history in which `preserves_original` is always true. A corrected observation must be represented by a successor/correction record; original observations are not silently rewritten.

## Deliberate omissions

Phase 1 does not implement semantic search, automatic deduplication, research ranking, MEV scoring, budget optimization, L2/L3 authorization, commercial prioritization, UI, or database infrastructure.
