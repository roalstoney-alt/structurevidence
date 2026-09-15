# CML StructEvidence Integration Assessment v0.1

## Architecture Decision

`ONE EVIDENCE CORE + SHARED STORAGE + DOMAIN-SPECIFIC TECHNICAL RISK MODULE`

### A. Reused primitives

RTP-style source/artifact lineage, append-only event semantics, dual clocks, corrections, directional supersession, RDL freshness states, GDR release authorization, Verify and hash-bound manifests.

### B. Domain data that does not fit structural-dynamics objects

Exact manufacturer identity, package/interface, lifecycle state, replacement relationships, compatibility cells, qualification scope and test requirements. These belong to a domain payload, not crypto/network research dimensions.

### C. Why a domain module is required

CML owns technical vocabularies and validation laws while the Evidence Core owns provenance, time, correction, supersession, release and integrity.

### D. Why no separate evidence database is required

Every CML record uses the same common record envelope and file-backed canonical storage conventions. A second provenance, event, freshness or Verify system would create conflicting truth histories.

### E. Shared schemas

`evidence/core/schema/evidence_core_record.schema.json` defines identifiers, source/artifact references, effective/known time, verification, correction, supersession, policy and hashes.

### F. CML-specific schemas

Technical Item, Event, Candidate, Compatibility, Test Requirement, Public Record, Release Manifest and Snipe Report.

### G. RDL Freshness reuse

RDL v0.1a states and precedence are reused. CML adds family-specific profiles; no global component age threshold exists. Where cadence is unsupported the result is `POLICY_NOT_CONFIGURED`.

### H. GDR-SE reuse

GDR remains the release/paid-delivery veto layer. CML v0.1 maps technical primary-source coverage, counter-evidence, unresolved qualification gaps, correction, supersession and freshness into a domain adapter. No paid/current authorization is self-awarded.

### I. Frozen semantics

LEVEL, DELTA, NO OBSERVATION, EVENT TIME, KNOWLEDGE TIME, CORRECTION and SUPERSESSION are unchanged. Existing digital-asset payloads and findings are untouched.

### J. Future client BOM migration

Private ingestion must normalize manufacturer + exact MPN without destructive merging, match the Technical Item registry, run lifecycle/dependency clustering, and publish only authorized derived metadata. Private BOM fields never enter Public Verify.

## Cross-domain future

The shared grammar is `Identity -> Event -> Dependency -> Evidence -> Alternative -> Verification -> Decision`. Future catalysts, specialty chemicals, APIs, optics, motors and bearings add domain profiles and typed fields, not new evidence cores or websites.
