# OIL-GENESIS-001 Evidence Request Matrix

Stage: `STAGE 3 — CONTROLLED SUPPLIER EVIDENCE REQUEST`  
Domain: `OIL-DOMAIN-001 — Reinforced Platinum-Cured Silicone Hose`  
Created as of: `2026-10-03`  
Execution state: `PREPARED — NOT SENT`

## Operating principle

The supplier does not define what counts as proof. StructEvidence defines each frozen Claim, its scope, acceptable evidence, non-qualifying evidence, and stop conditions. The supplier may submit evidence, correct scope, narrow or withdraw a claim, or state that evidence is unavailable.

`SUPPLIER_STATEMENT_ALONE != SUPPORTED`

A casual email, sales reply, or verbal statement may establish claim origin or source attribution, but cannot by itself assign a capability status. A formal `MANUFACTURER_DECLARATION` is evaluated as an artifact only when it identifies the accountable issuer, exact product/material scope, claim scope, date/revision, and declaration basis.

Stage 3 does not ingest evidence or assign `SUPPORTED`, `OBSERVED`, `UNKNOWN`, `NOT_ESTABLISHED`, or `CONTRADICTED`.

## Shared scope rule

Where applicable, submitted evidence must identify:

- provider/manufacturer;
- product family and product series;
- configuration and size;
- test/rating conditions and method;
- certificate/declaration scope;
- issuer and source;
- document date/revision.

Never generalize one product family to the entire company, one size to all sizes, one certificate to all product lines, one test condition to all conditions, or one factory to every manufacturing site.

## Shared verification stop rule

Future verification stops at the first documented terminal condition:

- `QUALIFYING_DOCUMENT`
- `TWO_INDEPENDENT_SOURCES`
- `INSUFFICIENT_EVIDENCE`
- `MAX_VERIFICATION_TIME` — four human hours per claim

Stage 3 only requests evidence; it does not execute these verification decisions.

## Claim matrix

### OIL-CAP-SIL-001 — platinum-cured system

**Claim:** Provider evidence supports that the referenced hose or product family uses a platinum-cured silicone system.

**Scope:** Referenced hose/product family and documented formulation or manufacturing scope only.

**Acceptable evidence types:** `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DATASHEET`, `MANUFACTURER_DECLARATION`, `FACTORY_DOCUMENT`.

**Minimum scope/identifiers:** manufacturer; product/family; platinum-cured material/process; issuer; document identifier; date/revision.

**Non-qualifying alone:** sales email; marketing phrase; marketplace/reseller listing; generic silicone statement.

**Do not infer:** reinforcement, pressure, temperature, or food-contact compliance.

### OIL-CAP-SIL-002 — reinforced construction

**Claim:** Provider evidence supports reinforced construction for the referenced silicone hose or product family.

**Scope:** Referenced construction/product family and documented reinforcement type only.

**Acceptable evidence types:** `MANUFACTURER_DATASHEET`, `FACTORY_DOCUMENT`, `THIRD_PARTY_TEST_REPORT`.

**Minimum scope/identifiers:** manufacturer; product/family; braid/textile/polyester/other reinforcement specification; issuer; document identifier; date/revision.

**Non-qualifying alone:** “heavy duty”; “high pressure”; “industrial hose”; an image without a construction specification.

### OIL-CAP-SIL-003 — working pressure at least 9 bar

**Claim:** Provider evidence supports a maximum working pressure of at least 9 bar for the referenced configuration under documented conditions.

**Scope:** Size, construction, temperature, medium, method, and stated operating conditions.

**Acceptable evidence types:** `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DATASHEET`, `FACTORY_DOCUMENT`.

**Minimum scope/identifiers:** hose series/configuration; ID/OD where applicable; reinforcement; working pressure value/unit; working-versus-burst distinction; rating/test temperature; issuer; method/basis; date/revision.

**Non-qualifying alone:** burst pressure; generic “high pressure”; unrelated series; sales statement without specification.

**Special rule:** Never transform burst pressure into working pressure without explicit manufacturer/test-method linkage.

### OIL-CAP-SIL-004 — lower operating bound at or below -40°C

**Claim:** Provider evidence supports an operating-temperature lower bound at or below -40°C for the referenced product family under documented conditions.

**Acceptable evidence types:** `MANUFACTURER_DATASHEET`, `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DECLARATION`, `FACTORY_DOCUMENT`.

**Minimum scope/identifiers:** product/material family; temperature/unit; whether the value is operating, temporary exposure, storage, or a test condition; issuer; date/revision.

**Non-qualifying alone:** storage limit presented as operating; test condition presented as continuous operation; unrelated material/series; unscoped sales statement.

### OIL-CAP-SIL-005 — upper operating bound at or above +180°C

**Claim:** Provider evidence supports an operating-temperature upper bound at or above +180°C for the referenced product family under documented conditions.

**Acceptable evidence types:** `MANUFACTURER_DATASHEET`, `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DECLARATION`, `FACTORY_DOCUMENT`.

**Minimum scope/identifiers:** product/material family; temperature/unit; continuous, short-term, sterilization, storage, or test-condition classification; issuer; date/revision.

**Non-qualifying alone:** sterilization excursion or storage limit presented as continuous operation; unrelated material/series; unscoped sales statement.

### OIL-CAP-SIL-006 — qualifying 21 CFR 177.2600 documentation

**Claim:** The referenced product family has qualifying documentation addressing 21 CFR 177.2600 for the documented material, article, food-contact use, extraction conditions, and date scope.

**Acceptable evidence types:** `THIRD_PARTY_CERTIFICATE`, `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DECLARATION`.

**Minimum scope/identifiers:** regulation reference; product/material; issuer/laboratory; document identifier; date/revision; test or declaration basis.

**Non-qualifying alone:** “FDA grade”; “FDA approved”; “food grade”; sales email; catalog badge without supporting scope.

**Special rule:** Do not characterize the result as FDA approval or extend it beyond the source scope.

### OIL-CAP-SIL-007 — qualifying EC 1935/2004 documentation

**Claim:** The referenced product family has qualifying documentation addressing Regulation (EC) No 1935/2004 for the documented material, article, intended food-contact application, and date scope.

**Acceptable evidence types:** `THIRD_PARTY_CERTIFICATE`, `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DECLARATION`.

**Minimum scope/identifiers:** regulation reference; material/product; intended food-contact use; issuer/laboratory; document identifier; date/revision; supporting regulatory references.

**Non-qualifying alone:** generic “EU compliant” or “food grade”; sales email; unsupported badge; declaration for unrelated material/product.

**Special rule:** Framework-regulation documentation does not automatically establish every material-specific EU requirement.

## Visibility consent model

Every evidence item must select one:

- `PUBLIC`: permits a limited public projection of claim, future status, as-of boundary, evidence type/identifier, and scope summary. The raw document need not be public.
- `AUTHORIZED_BUYER`: may later be shown only under a qualified Demand and proven authorization. Until that layer exists, fail closed and keep private.
- `TRANSACTION_PRIVATE`: restricted to an identified transaction or explicitly authorized party; never placed in public exports.

Unknown, incomplete, or contradictory consent fails closed to private storage.

## Supplier response options

For each requested claim the supplier may select:

- `EVIDENCE_ATTACHED`
- `PUBLIC_REFERENCE_PROVIDED`
- `CLAIM_SCOPE_CORRECTION`
- `CLAIM_WITHDRAWN`
- `EVIDENCE_UNAVAILABLE`
- `CONFIDENTIAL_ONLY`
- `NOT_APPLICABLE`

Scope correction and withdrawal are valid responses; they are not treated as capability failure.

## Historical record notice

Evidence submitted to StructEvidence creates a timestamped historical capability record if later accepted through the defined process. Each item retains its source, scope, date, and visibility. Future evidence and real-world outcomes may confirm, narrow, contradict, supersede scope, or remain incomparable without silently deleting or rewriting earlier records. A VerifiedCapabilityFact is not permanent truth.

Open Intent Lab does not create a universal supplier rating or paid ranking from these records.

## Consistency relation vocabulary — prepared only

- `CONFIRMS`
- `CONSISTENT_WITH`
- `PARTIALLY_CONSISTENT`
- `CONTRADICTS`
- `SUPERSEDES_SCOPE`
- `NOT_COMPARABLE`

No relation is created in Stage 3. `CONTRADICTS` requires sufficiently comparable product family, configuration, batch, factory, method, conditions, date, and source; otherwise `NOT_COMPARABLE` may be correct.

## Disclosure event vocabulary — prepared only

- `MATERIAL_FACT_NEWLY_DISCLOSED`
- `MATERIAL_SCOPE_CLARIFIED`
- `MATERIAL_SCOPE_RESTRICTED`
- `MATERIAL_CLAIM_CONTRADICTED`
- `MATERIAL_OUTCOME_DEVIATION`
- `EVIDENCE_UPDATED`
- `EVIDENCE_WITHDRAWN_BY_SOURCE`

No event is created in Stage 3. Event language records material information without inferring intent.

## Stage boundary

No evidence ingestion, file hashing, verification, VCF, production Provider, Demand, Outcome, ReuseRecord, migration, UI, deployment, or external transmission occurs in Stage 3. All packs remain drafts pending human review.

