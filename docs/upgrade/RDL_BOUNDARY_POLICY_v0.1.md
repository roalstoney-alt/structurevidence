# RDL Boundary Policy v0.1

## Evidence Core

RDL research records reuse `evidence/core/schema/evidence_core_record.schema.json`. No second provenance or evidence store is created.

## CML

CML remains authoritative for structural facts, PDRE status and migration readiness. RDL records what research happened and may reference before/after CML state. Every record is fixed to `structural_interpretation_authority = CML_REFERENCE_ONLY`.

## RTP

RTP-style manifests and existing hash verification remain authoritative for reproducibility. RDL may reference them through `rtp_refs`; it does not replace their verification functions.

## ECN/timeline

Existing timeline and monitoring transitions remain the canonical state-transition systems. RDL records the research-relevant decision delta and references authoritative state/timeline artifacts; it does not create another transition ledger.

## GDR-SE

RDL never grants publication, paid-delivery, production-release or L2/L3 authorization. L2/L3 records must represent external authorization state, and authorized records require a reference to the human/GDR authority.

## Privacy

Raw private prompts, credentials, API keys, customer secrets and unnecessary uploaded contents are prohibited. Customer-specific records may reference protected artifacts. Reusable inventory evidence must remain separable from private context.

## Historical records

No historical CML, RDL freshness, RTP-style manifest, ECN/timeline, GDR or research artifact is migrated or rewritten. Missing historical RDL research records mean `LEGACY / PRE-RDL-RESEARCH-RECORD`, not that no research occurred.

## Optimization boundary

Phase 1 observes. It does not rank research, calculate an opaque MEV score, optimize token budgets, authorize escalation, run semantic search-memory, or prioritize commercial work.
