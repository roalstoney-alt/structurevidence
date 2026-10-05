# OIL-GENESIS-001 Domain Freeze

This document freezes Stage 1 vocabulary and claim definitions only. It contains no provider selection, supplier fact, demand record, evidence record, ranking, or confidence score.

## DOMAIN_ID

`OIL-DOMAIN-001`

Domain version: `v0.1`  
Experiment: `OIL-GENESIS-001`  
Decision: `FREEZE`

## DOMAIN_NAME

Reinforced Platinum-Cured Silicone Hose

## WHY_SELECTED

The domain combines reusable construction, pressure, temperature, and food-contact documentation questions with bounded verification artifacts and observable downstream outcomes. It is narrow enough for a Genesis experiment but broad enough to avoid encoding one buyer's dimensions or order length.

Domain fitness result:

| Criterion | Result | Basis |
| --- | --- | --- |
| TESTABILITY | PASS | Construction can be checked through scoped documents and, where authorized, sample observation; pressure can be supported by hydrostatic test evidence; dimensions and length have established measurement methods. |
| EVIDENCE_ACCESSIBILITY | PASS | Datasheets, declarations, certificates, reports, factory documents, sample observations, buyer tests, and transaction outcomes are plausible evidence classes. Availability for a particular provider remains unproven until Stage 2+. |
| REUSE_POTENTIAL | PASS | Cure system, reinforcement, working pressure, temperature range, and scoped food-contact documentation recur across buyers and product families. |
| OUTCOME_OBSERVABILITY | PASS | Receipt, dimensional inspection, pressure/buyer testing, and transaction outcomes can later produce bounded observations without converting those observations into universal capability claims. |
| REGULATORY_FRICTION | PASS | Friction is material but manageable if every compliance conclusion is regulation-, product-, material-, application-, and date-scoped. PASS does not mean low friction or automatic compliance. |

Standards and regulation checks used only to establish domain viability:

- ISO 4671:2022 defines methods for measuring hose inside diameter, outside diameter, wall thickness, and length: <https://www.iso.org/standard/75826.html>.
- ISO 1402:2021 specifies hydrostatic testing methods for hose assemblies: <https://www.iso.org/standard/75827.html>.
- 21 CFR 177.2600 concerns rubber articles intended for repeated use in food manufacture, preparation, and transportation; it does not establish a generic product-wide “FDA certification”: <https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-177/subpart-C/section-177.2600>.
- Regulation (EC) No 1935/2004 is a framework regulation for food-contact materials and requires scope-specific safety and traceability reasoning: <https://eur-lex.europa.eu/eli/reg/2004/1935/oj>.

No supplier search was performed.

## TESTABILITY

PASS. Each frozen claim has a normalized operator/value and a bounded evidence route. A claim may terminate as `NOT_ESTABLISHED` when the authorized evidence envelope is exhausted; testability does not guarantee support.

## EVIDENCE_ACCESSIBILITY

PASS, conditionally. The vocabulary anticipates both public and private evidence. Private availability must be authorized and is not inferred from the existence of a demand or provider record.

## REUSE_POTENTIAL

PASS. Exact geometry and order-length constraints are deliberately excluded from the Genesis dictionary so that the frozen claims can be reused across multiple future buyer demands.

## OUTCOME_OBSERVABILITY

PASS. Later stages can observe delivered geometry, sample construction, buyer test results, and transaction outcomes. An outcome must pass normal evidence review before it may support a canonical claim.

## REGULATORY_FRICTION

PASS with strict scope controls. Compliance claims assert only the existence of qualifying documentation for the referenced product or material scope. Marketing phrases, logos, or unspecific “food grade”/“FDA grade” statements are insufficient.

`2007/19/EC` is not retained as a Genesis claim: Commission Directive 2007/19/EC amended the former plastics Directive 2002/72/EC, which Regulation (EU) No 10/2011 later repealed from 1 May 2011. Any historical relevance must be assessed for a specific demand and document, not frozen as a general silicone-hose capability. Sources: <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32007L0019> and <https://eur-lex.europa.eu/eli/reg/2011/10/oj>.

`AS 2069` is not retained because the exact reference and applicability were not established from an authoritative source. The official Standards Australia page identifies AS 2070 as the standard concerning plastics materials for food contact, but that does not justify silently substituting AS 2070 for the supplied candidate: <https://www.standards.org.au/standards-catalogue/standard-details?designation=as-2070-1999>.

## FROZEN_CLAIM_DICTIONARY

All claims are either `TECHNICAL_CAPABILITY` or `COMPLIANCE_EVIDENCE`. A compliance artifact never establishes manufacturing capability outside its stated scope.

### OIL-CAP-SIL-001 — platinum_cured

- **type:** `TECHNICAL_CAPABILITY`
- **normalized_claim:** Provider evidence supports that the referenced hose or product family uses a platinum-cured silicone system.
- **scope:** Referenced hose/product family and the documented formulation or manufacturing scope only.
- **unit / operator / value:** `ENUM` / `EQ` / `PLATINUM_CURED`
- **evidence_examples:** scoped manufacturer datasheet; manufacturer declaration; factory document; third-party test report that identifies the relevant product and cure system.
- **prohibited_overinterpretation:** Do not infer medical grade, peroxide-free status, food-contact compliance, purity, extractables performance, or every product made by the provider.

### OIL-CAP-SIL-002 — reinforced_construction

- **type:** `TECHNICAL_CAPABILITY`
- **normalized_claim:** Provider evidence supports reinforced construction for the referenced silicone hose or product family.
- **scope:** Referenced construction/product family and documented reinforcement type only.
- **unit / operator / value:** `ENUM` / `EQ` / `REINFORCED`
- **evidence_examples:** scoped datasheet; construction drawing; factory document; third-party report; authorized physical sample observation.
- **prohibited_overinterpretation:** Do not infer reinforcement material, braid count, pressure rating, burst pressure, kink resistance, or performance of another series.

### OIL-CAP-SIL-003 — maximum_working_pressure

- **type:** `TECHNICAL_CAPABILITY`
- **normalized_claim:** Provider evidence supports a maximum working pressure of at least 9 bar for the referenced hose configuration under the documented conditions.
- **scope:** Referenced size, construction, temperature, medium, test method, and other stated operating conditions.
- **unit / operator / value:** `bar` / `GTE` / `9`
- **evidence_examples:** third-party hydrostatic test report; scoped manufacturer datasheet; factory test document with method and conditions.
- **prohibited_overinterpretation:** Do not infer burst pressure, proof pressure, safety factor, vacuum rating, dynamic impulse life, or unrelated size/series performance.

### OIL-CAP-SIL-004 — minimum_operating_temperature

- **type:** `TECHNICAL_CAPABILITY`
- **normalized_claim:** Provider evidence supports an operating-temperature lower bound at or below -40 °C for the referenced hose or product family under documented conditions.
- **scope:** Referenced product family, medium, duration, pressure/installation conditions, and definition of operating temperature.
- **unit / operator / value:** `degC` / `LTE` / `-40`
- **evidence_examples:** scoped datasheet; manufacturer declaration; third-party test report; factory test document.
- **prohibited_overinterpretation:** Do not infer continuous service duration, pressure retention at -40 °C, sterilization performance, or fitness for every medium.

### OIL-CAP-SIL-005 — maximum_operating_temperature

- **type:** `TECHNICAL_CAPABILITY`
- **normalized_claim:** Provider evidence supports an operating-temperature upper bound at or above +180 °C for the referenced hose or product family under documented conditions.
- **scope:** Referenced product family, medium, duration, pressure/installation conditions, and definition of operating temperature.
- **unit / operator / value:** `degC` / `GTE` / `180`
- **evidence_examples:** scoped datasheet; manufacturer declaration; third-party test report; factory test document.
- **prohibited_overinterpretation:** Do not infer continuous service duration, pressure retention at +180 °C, steam/sterilization cycles, or fitness for every medium.

### OIL-CAP-SIL-006 — fda_21_cfr_177_2600_documentation

- **type:** `COMPLIANCE_EVIDENCE`
- **normalized_claim:** The referenced product family has qualifying documentation addressing 21 CFR 177.2600 for the documented material, article, food-contact use, extraction conditions, and date scope.
- **scope:** Exact documented product/material/application and applicable conditions only.
- **unit / operator / value:** `REGULATORY_REFERENCE` / `QUALIFYING_DOCUMENT_FOR_SCOPE` / `21_CFR_177_2600`
- **evidence_examples:** current third-party test report; scoped manufacturer declaration linked to underlying test or formulation evidence; qualifying certificate whose issuer, subject, method, and date are verifiable.
- **prohibited_overinterpretation:** Do not call this an FDA approval or certification; do not infer compliance for undocumented formulations, articles, food types, temperatures, extraction conditions, or dates.

### OIL-CAP-SIL-007 — ec_1935_2004_documentation

- **type:** `COMPLIANCE_EVIDENCE`
- **normalized_claim:** The referenced product family has qualifying documentation addressing Regulation (EC) No 1935/2004 for the documented material, article, intended food-contact application, and date scope.
- **scope:** Exact documented product/material/application and applicable supporting measures only.
- **unit / operator / value:** `REGULATORY_REFERENCE` / `QUALIFYING_DOCUMENT_FOR_SCOPE` / `EC_1935_2004`
- **evidence_examples:** scoped declaration of compliance where applicable; third-party migration/test report; manufacturer declaration tied to product identity and supporting evidence.
- **prohibited_overinterpretation:** Do not infer universal EU food-contact compliance, compliance with every material-specific measure, every migration limit, GMP, or suitability for undocumented conditions.

## DEFERRED_CLAIMS

| Candidate | Disposition | Rationale |
| --- | --- | --- |
| C3 — ID 6 mm / OD 12 mm | `DEFER_TO_DEMAND` | Independently measurable but encodes one demand's exact geometry rather than reusable Genesis capability. Preserve ID and OD as separate demand constraints when used. |
| C5 — 25 m continuous length | `DEFER_TO_DEMAND` | Commercially meaningful and measurable but order-/buyer-specific. Preserve “continuous” explicitly; do not treat aggregate length as equivalent. |

## REMOVED_CLAIMS

| Candidate | Disposition | Rationale |
| --- | --- | --- |
| C4 — 3 mm wall thickness | `REMOVE` | Redundant with C3's nominal ID/OD for this RFQ and too configuration-specific. Never derive actual wall thickness from nominal diameters without the relevant tolerance/measurement basis. |
| C11 — 2007/19/EC documentation | `REMOVE` | Legacy amendment in the former EU plastics regime; unsuitable as a stable standalone Genesis claim for silicone hose. May be evaluated if a later demand presents a historically relevant document. |
| C12 — AS 2069 documentation | `REMOVE` | Exact authoritative reference and applicability were not established. Do not silently correct or substitute a different standard. |

Candidate disposition summary: C1, C2, C6, C7, C8, C9, C10 `KEEP_FOR_GENESIS`; C3, C5 `DEFER_TO_DEMAND`; C4, C11, C12 `REMOVE`.

## CLAIM_ID_CONVENTION

`OIL-CAP-SIL-NNN`

- `OIL`: Open Intent Lab namespace.
- `CAP`: reusable capability/compliance-claim namespace; the claim itself is not a fact.
- `SIL`: stable domain mnemonic for the silicone-hose Genesis domain.
- `NNN`: zero-padded, append-only ordinal.

IDs are supplier- and demand-independent. A semantic change creates a new ID or a new dictionary version; historical facts are never rewritten to acquire the new meaning.

## UNIT_NORMALIZATION

- Pressure canonical unit: `bar`; preserve the original value/unit and conversion provenance. `1 bar = 100,000 Pa` exactly.
- Temperature canonical unit: `degC`; preserve the original value/unit and conversion provenance. Fahrenheit conversion is `°C = (°F - 32) × 5/9`.
- Categorical construction claims: unit `ENUM`, operator `EQ`.
- Compliance-document claims: unit `REGULATORY_REFERENCE`, operator `QUALIFYING_DOCUMENT_FOR_SCOPE`; regulation identifiers remain exact strings.
- Deferred diameter/wall dimensions, if activated by a demand: canonical `mm`; preserve tolerances and measurement method.
- Deferred continuous length, if activated by a demand: canonical `m`; preserve “continuous” as a constraint.
- Never derive wall thickness, working pressure, or compliance from another normalized field unless an explicit reviewed rule and evidence support that conclusion.

## STATUS_MAPPING

The canonical stored epistemic states are one-to-one StructEvidence/OIL states:

| OIL conceptual term | Canonical representation |
| --- | --- |
| `SUPPORTED` | `SUPPORTED` |
| `OBSERVED` | `OBSERVED` |
| `UNKNOWN` | `UNKNOWN` |
| `NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| `CONTRADICTED` | `CONTRADICTED` |

`SUPPORTED` records qualifying documentary or test support for the normalized claim. It does not mean that the capability was observed in an actual transaction.

`OBSERVED` records a direct, bounded real-world observation such as a physical sample observation, buyer-side test, transaction outcome, delivery performance, or acceptance result. Every `OBSERVED` record must retain `observation_scope`, `source`, `as_of`, and the related demand/outcome where applicable. Observation alone does not generalize to all product families, batches, factories, or future production.

Status history is append-only. A capability may have a `SUPPORTED` record at T1 and a later `OBSERVED` record at T2; both remain addressable and neither overwrites the other. A contradictory observation also remains an `OBSERVED` event. It may support a newer claim-level `CONTRADICTED` decision, but the underlying observation and the older support record are not deleted or rewritten.

Workflow labels such as `VERIFICATION_REQUIRED` are not epistemic states. These five values are one controlled canonical vocabulary, not parallel truth models.

## AS_OF_RULE

Every evidence item retains its own event/publication time and `known_at` time. Every `OBSERVED` event separately retains its actual observation date. For a reviewed VerifiedCapabilityFact version:

`as_of = the latest relevant conclusion boundary supported by only the evidence and observations used in that VCF version`

The deterministic boundary is the maximum relevant `known_at`/observation time among those inputs, with the conclusion/review time stored separately. Adding later evidence or an observation appends a new VCF version or superseding conclusion; it does not rewrite the historical `as_of`. A newer `as_of` never implies that older evidence was revalidated at that date. The field never means `valid_forever` or `currently_true`. If an input's relevant time is unknown, the conclusion must disclose the limitation and cannot fabricate a date.

## VISIBILITY_ENUM

Frozen enum:

- `PUBLIC` — former OIL L0.
- `AUTHORIZED_BUYER` — former OIL L1.
- `TRANSACTION_PRIVATE` — former OIL L2.

These names replace ambiguous L0/L1/L2 visibility labels and do not alter OIL-DPE v0.4 meaning. Existing storage terminology such as `CUSTOMER_PRIVATE` may be adapted later, but it is not a fourth Stage 1 visibility level.

## ACCESS_FAIL_CLOSED_RULE

If authorization cannot be proven for the subject, object, scope, and time of access, access is denied and the evidence remains private. The existence of a demand, buyer, provider, capability fact, or transaction is not authorization. Unknown or absent visibility metadata is never treated as `PUBLIC`.

## PROVIDER_MINIMUM_FIELDS

Frozen for later implementation only; no provider records are created in Stage 1:

- `provider_id`
- `legal_name`
- `trading_name` (nullable)
- `jurisdiction`
- `official_domain` (nullable until verified)
- `identity_evidence_refs`
- `provider_status`: `IDENTITY_UNVERIFIED`, `IDENTITY_VERIFIED`, or `INACTIVE`
- `created_at`

This is an identity link sufficient to answer which legal/commercial entity a fact belongs to. It is not KYC/KYB scoring.

## DEMAND_TYPES

Frozen types: `EXTERNAL_DEMAND`, `OPERATOR_DEMAND`.

Minimum later fields: `demand_id`, `demand_type`, `principal_ref`, `created_at`, `decision_window`. No demand records are created in Stage 1.

## FACT_ORIGIN_ENUM

- `GENESIS_SUBMISSION` — controlled initial submission/intake.
- `SUPPLIER_UPDATE` — later provider-originated update.
- `DEMAND_TRIGGERED` — verification initiated by a demand.
- `OUTCOME_GENERATED` — evidence arising from an observed outcome, after review.
- `STRUCTEVIDENCE_RESEARCH` — independent StructEvidence research.

Origin records how a fact investigation began; it is not evidence strength, status, provenance, or visibility.

## EVIDENCE_TYPE_MAPPING

| OIL evidence type | Canonical handling |
| --- | --- |
| `THIRD_PARTY_CERTIFICATE` | Evidence/source record with issuer, subject, scope, dates, and artifact provenance; third-party label alone does not establish independence. |
| `THIRD_PARTY_TEST_REPORT` | Evidence/source record with laboratory, method, sample/product identity, conditions, results, and dates. |
| `MANUFACTURER_DATASHEET` | Primary manufacturer statement; preserve product/version/date scope. |
| `MANUFACTURER_DECLARATION` | Primary manufacturer statement; preserve signatory, legal entity, product/material, regulatory scope, and date. |
| `FACTORY_DOCUMENT` | Primary or private factory artifact; preserve issuer, object, method, and visibility. |
| `PHYSICAL_SAMPLE_OBSERVATION` | Observation evidence limited to the inspected sample/configuration and observation conditions. |
| `BUYER_TEST` | Buyer-generated test evidence with method, sample identity, conditions, authorization, and result. |
| `TRANSACTION_OUTCOME` | Outcome record that may become evidence only after canonical review/provenance handling. |
| `PUBLIC_CORPORATE_RECORD` | Public identity/corporate source; authority depends on issuer and jurisdiction. |

No evidence type is itself a status. Evidence and provenance remain canonical StructEvidence records; a VerifiedCapabilityFact references them rather than duplicating their truth content.

## STOP_POINT_RULES

Verification for each claim stops at the first documented terminal condition:

- `QUALIFYING_DOCUMENT`: an authorized, authenticatable artifact matches the exact provider/product/configuration, claim scope, method/conditions where relevant, and usable date scope.
- `TWO_INDEPENDENT_SOURCES`: two genuinely independent sources meet the predeclared corroboration rule when no single qualifying document is sufficient. Two copied claims or two documents with a common unexamined origin are not independent.
- `INSUFFICIENT_EVIDENCE`: the authorized search/evidence envelope is exhausted without enough support; record `NOT_ESTABLISHED` or `UNKNOWN` as appropriate, never optimistic support.
- `MAX_VERIFICATION_TIME`: stop at 4 human hours per claim, record what was checked and the unresolved gap.

Claim-specific qualifying-document emphasis:

- OIL-CAP-SIL-001/002: exact product-family construction/formulation scope.
- OIL-CAP-SIL-003: exact configuration and pressure/test conditions.
- OIL-CAP-SIL-004/005: operating versus intermittent/peak definition, medium, duration, pressure, and installation conditions.
- OIL-CAP-SIL-006/007: exact product/material/application, applicable regulation, supporting tests/declarations, issuer, and date; generic badges and marketing language do not qualify.

The 4-hour ceiling cannot be changed without human approval.

## OPEN_GAPS

- No provider, product family, artifact, or supplier evidence has been evaluated; all future fact statuses begin unknown.
- The later implementation must define authorization storage/enforcement for `AUTHORIZED_BUYER` and `TRANSACTION_PRIVATE` evidence.
- The exact applicability of material-specific EU measures to a future silicone-hose product and intended use must be reviewed case by case.
- The intended Australian food-contact reference behind “AS 2069” remains unresolved; no substitution is authorized.
- Test methods and acceptance conditions for temperature capability need to be chosen per future product configuration and demand.
- Stage 2 requires a separate human gate; this freeze does not authorize supplier discovery.
