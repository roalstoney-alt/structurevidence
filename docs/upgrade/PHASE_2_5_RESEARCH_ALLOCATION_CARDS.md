# Phase 2.5 Research Allocation Cards

Canonical machine-readable cards: `rdl/research/allocation/CML_PDRE_001_PHASE_2_5_ALLOCATION.json`.

## L1-CANDIDATE-001 — Application qualification

- Current state: `INSUFFICIENT_QUALIFICATION_EVIDENCE`
- Decision affected: whether readiness beyond R3 can be evaluated
- Proceed without research: `PARTIALLY`
- Minimum evidence: one independently attributable qualification result for a human-selected bounded requirement set
- Source class: `INDEPENDENT_QUALIFICATION_SOURCE`
- Scope: `BOUNDED_MULTI_SOURCE`
- Information gain / decision impact / reuse: `HIGH / HIGH / HIGH`
- Commercial relevance: `UNKNOWN`
- Future costs: `UNKNOWN`
- Stop: when the bounded requirement set has an attributable result, or an authorized bounded review establishes the source class is unavailable
- Codex recommendation: `DEFER_L2_REVIEW`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

## L1-CANDIDATE-002 — Production or field deployment

- Current state: `CONTRADICTORY_EVIDENCE`
- Decision affected: whether R5 `FIELD_DEPLOYED` can be evaluated
- Proceed without research: `PARTIALLY`
- Minimum evidence: one dated, independently attributable production-deployment or field-operation record
- Source class: `FIELD_DEPLOYMENT_SOURCE`
- Scope: `VERY_NARROW`
- Information gain / decision impact / reuse: `HIGH / HIGH / HIGH`
- Commercial relevance: `UNKNOWN`
- Future costs: `UNKNOWN`
- Stop: when one authoritative source confirms or refutes deployment, or an authorized bounded search cannot locate that source class
- Codex recommendation: `L1_VERIFY`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

## L1-CANDIDATE-003 — Independent support for three claims

- Current state: `INSUFFICIENT_INDEPENDENCE`
- Decision affected: whether copper, rack-space, and efficiency claims can be stronger than attributed source claims
- Proceed without research: `YES`
- Minimum evidence: one independent technical source or approved test artifact for each human-selected claim
- Source class: `PRIMARY_TECHNICAL_SOURCE`
- Scope: `BOUNDED_MULTI_SOURCE`
- Information gain / decision impact / reuse: `MEDIUM / MEDIUM / MEDIUM`
- Commercial relevance: `UNKNOWN`
- Future costs: `UNKNOWN`
- Stop: per selected claim, when one independent source confirms or refutes it, or the bounded review cannot obtain that source class
- Codex recommendation: `DEFER_L2_REVIEW`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

## L1-CANDIDATE-004 — Supplier, manufacturing, and capacity

- Current state: `MISSING_EVIDENCE`
- Decision affected: whether supply and manufacturing readiness can move beyond `UNKNOWN`
- Proceed without research: `PARTIALLY`
- Minimum evidence: a human-bounded set of manufacturing and supplier-capacity records distinguishing announced from qualified available capacity
- Source class: `MANUFACTURING_SOURCE_AND_SUPPLIER_CAPACITY_SOURCE`
- Scope: `BOUNDED_MULTI_SOURCE`
- Information gain / decision impact / reuse: `HIGH / MEDIUM / MEDIUM`
- Commercial relevance: `UNKNOWN`
- Future costs: `UNKNOWN`
- Stop: when each selected dimension has one attributable source, or an authorized bounded review establishes unavailability
- Codex recommendation: `DEFER_L2_REVIEW`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

## L1-CANDIDATE-005 — PDRE-001B facility-level chain

- Current state: `MISSING_EVIDENCE`
- Decision affected: whether PDRE-001B can move from active subhypothesis to an assessed candidate
- Proceed without research: `YES`
- Minimum evidence: a bounded packet covering the facility old path, alternative path, dependency transfer, readiness chain, provenance, and time
- Source class: `PRIMARY_TECHNICAL_SOURCE`
- Scope: `BOUNDED_MULTI_SOURCE`
- Information gain / decision impact / reuse: `HIGH / HIGH / HIGH`
- Commercial relevance: `UNKNOWN`
- Future costs: `UNKNOWN`
- Stop: when the human-approved packet represents every required chain stage, or an authorized bounded review establishes source unavailability
- Codex recommendation: `DEFER_L2_REVIEW`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

## L1-CANDIDATE-006 — Source lineage

- Current state: `INSUFFICIENT_INDEPENDENCE`
- Decision affected: whether repeated claims count as independent confirmation
- Proceed without research: `YES`
- Minimum evidence: lineage metadata linking each fixed evidence item to an original or derivative source
- Source class: `OTHER_SOURCE_LINEAGE_METADATA`
- Scope: `NARROW`
- Information gain / decision impact / reuse: `MEDIUM / LOW / HIGH`
- Commercial relevance: `NONE`
- Future costs: `UNKNOWN`
- Stop: when lineage is established for all seven items, or an authorized bounded metadata review cannot resolve it
- Codex recommendation: `WATCH`
- Authorization / human decision: `PENDING_HUMAN_DECISION / PENDING`

No card answers its technical question or authorizes research.
