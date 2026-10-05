# OIL-GENESIS-001 — Human Outreach Review

**Stage:** `STAGE 3 — HUMAN OUTREACH REVIEW PREP`  
**Prepared as of:** `2026-10-03`  
**Decision owner:** Human reviewer  
**External transmission:** None

## Review objective

Determine whether each frozen Genesis candidate is sufficiently well-defined to receive its existing controlled evidence request. This review does not rank suppliers, verify capability, assign a capability status, authorize sending, or send any message.

`SEND_AUTHORIZED = NO`  
`MESSAGES_SENT = 0`  
`SEND_APPROVAL = UNSET FOR ALL FIVE`

## Review method and boundary

Stage 2 candidate records and Stage 3 packs were the primary inputs. Limited current verification was restricted to official legal, corporate, product, technical and contact sources for the same five candidates. No replacement supplier search was performed.

Brand, legal entity, manufacturer and contracting entity were not treated as interchangeable. Public product material remains a discovery signal; it was not ingested as Evidence and created no Provider, VerifiedCapabilityFact, Demand, Outcome or ReuseRecord.

## Consolidated review

| Candidate | Identity | Contact | Claims | Evidence Threshold | Major Risk | Human Decision |
| --- | --- | --- | ---: | --- | --- | --- |
| `OIL-CAND-001` Venair | `CONFIRMED` | `CONFIRMED` — official sales email | 7 retained | Appropriate | Exact manufacturing site and regulatory artifact scope | `UNSET` |
| `OIL-CAND-002` Saint-Gobain | `CONFIRMED`; exact site partial | `CONFIRMED` — Bioprocess Application Support/Quality form | 7 retained | Appropriate if series remain separate | SPT-70 FB IB and STHT-R signals must not be merged | `UNSET` |
| `OIL-CAND-003` AdvantaPure | `CONFIRMED` | `CONFIRMED` — official compliance email | 6 retained | Appropriate; Claim 006 scope mapping required | Archived APSH evidence may not map to current APSH-P | `UNSET` |
| `OIL-CAND-004` WMFTS/BioPure | `CONFIRMED` | `USABLE_WITH_LIMITATION` — official directory, region not frozen | 5 retained | Appropriate | Manufacturer and regional contracting seller may differ | `UNSET` |
| `OIL-CAND-005` Trelleborg | `PARTIAL` | `CONFIRMED` — current Medical Solutions form | 5 conditionally retained | Scope ambiguous | Legal operator/site and PharmaSil/200 HP/BioPharmaPro mapping unresolved | `UNSET` |

## Candidate recommendations

### OIL-CAND-001 — Venair Ibérica SAU

`CODEX_PREP_RECOMMENDATION = READY_FOR_HUMAN_DECISION`

The legal website owner, official domain, product family and published sales route are attributable. All seven claims have a product-family public signal. The evidence request properly asks for size/condition scope and underlying regulatory artifacts rather than relying on the public statements alone.

Human review should confirm whether the exact manufacturing site matters for the first request and whether seven claims is acceptable in one exchange.

### OIL-CAND-002 — Saint-Gobain Performance Plastics Corporation

`CODEX_PREP_RECOMMENDATION = READY_FOR_HUMAN_DECISION`

The official Bioprocess legal notice identifies the North American Life Sciences business and website owner. The current Bioprocess contact form supports Application Support and Quality routing and is more specific than the broader Medical form in the draft.

All seven claims remain supportable as requests only if the existing product-family boundary is preserved: SPT-70 FB IB supports the construction, pressure and regulatory signals; STHT-R supplies separate temperature signals. No combined capability conclusion is allowed.

### OIL-CAND-003 — NewAge Industries, Inc. / AdvantaPure

`CODEX_PREP_RECOMMENDATION = READY_FOR_HUMAN_DECISION`

The brand-parent-manufacturer relationship is attributable, and AdvantaPure publishes an official compliance address suited to evidence questions. Six claim requests remain in scope. Claim 006 is intentionally conditional: an archived APSH regulatory reference must be mapped to the current APSH-P product/revision before it can qualify.

### OIL-CAND-004 — Watson-Marlow Flow Smart, Inc. / BioPure

`CODEX_PREP_RECOMMENDATION = READY_FOR_HUMAN_DECISION`

Official BioPure material attributes the reviewed hose manufacturing scope to Watson-Marlow Flow Smart, Inc. The global directory identifies BioPure-capable WMFTS offices, but the final region and recipient remain unfrozen; this is a contact limitation, not an identity failure. The five technical claims and their thresholds are appropriately scoped.

### OIL-CAND-005 — Trelleborg Medical Solutions

`CODEX_PREP_RECOMMENDATION = HOLD_FOR_CLARIFICATION`

Trelleborg Medical Solutions is a defined business area and has a current official product/engineering form. Public sources do not identify the exact legal manufacturing or contracting entity for the requested hose. In addition, Stage 2 material references PharmaSil and 200 HP while current 2026 material presents BioPharmaPro braided reinforced hose. The five claim requests are held until one current series, legal operator/site and route-to-contracting entity are clearly separated or mapped.

Trelleborg AB (publ) is the parent group and is not presumed to be the manufacturer or contracting entity.

## Claims and threshold review

- Claim/supplier pairs reviewed: `30/30`.
- Claims removed: `0`.
- Claims reworded in this prep stage: `0`.
- All requested Claim IDs remain within the seven Stage 1 frozen claims.
- Trelleborg's five requests are held, not removed; exact series-level wording must be frozen after clarification.
- Claim 003 always distinguishes working pressure from burst, proof and test pressure and requests size/configuration, temperature and method/basis.
- Claims 004 and 005 distinguish continuous operation, intermittent/sterilization exposure, storage and test conditions.
- Claim 006 requires 21 CFR 177.2600-specific issuer, product/material, date and basis; generic FDA wording is insufficient.
- Claim 007 is limited to the frozen Regulation (EC) No 1935/2004 documentation claim and does not imply full EU material-specific compliance.

## Supplier-facing safeguards

All five packs:

- offer `PUBLIC`, `AUTHORIZED_BUYER` and `TRANSACTION_PRIVATE` evidence visibility;
- fail closed when authorization is unclear;
- separate visibility from claim truth;
- explain timestamped, scoped history and preservation of later differences;
- avoid marketplace, certification, purchase, ranking and preferred-supplier promises; and
- prefer existing scoped documents over unrelated catalogs or broad disclosure.

The final outreach-preparation pass should explicitly retain “existing documents preferred; no bespoke report required; one clarification round” in the frozen message where space allows.

## Burden summary

| Burden | Candidates | Basis |
| --- | --- | --- |
| `LOW` | OIL-CAND-004 | Five technical claims with existing official product/validation material |
| `MODERATE` | OIL-CAND-001, OIL-CAND-002, OIL-CAND-003, OIL-CAND-005 | Six or seven claims, multiple series/regulatory scope, or identity clarification |
| `HIGH` | None | No pack requires bespoke testing or a complete document library |

## Official-source verification notes

- Venair's official legal notice identifies Venair Ibérica SAU; its product page and current datasheet cover VENABIO Technosil and publish a sales route.
- Saint-Gobain's official Bioprocess legal notice identifies Saint-Gobain Performance Plastics Corporation; its current contact form includes Application Support and Quality paths.
- AdvantaPure's official company page ties the brand to NewAge Industries, Inc.; its quality policy publishes `compliance@newageindustries.com`.
- WMFTS's official directory identifies BioPure-capable offices; official validation material attributes the reviewed manufacturing scope to Watson-Marlow Flow Smart, Inc.
- Trelleborg's official business-area and contact pages confirm Medical Solutions and its form, while current 2026 product literature exposes unresolved series/legal-operator mapping.

The exact official URLs and candidate-specific findings are retained in each review card and `human-review-prep.json`.

## Human decision gate

The human reviewer must set exactly one value for each candidate: `YES`, `NO`, or `HOLD`.

```text
OIL-CAND-001 = UNSET
OIL-CAND-002 = UNSET
OIL-CAND-003 = UNSET
OIL-CAND-004 = UNSET
OIL-CAND-005 = UNSET
```

No supplier may proceed to final outreach authorization until its human decision is `YES`. Sending remains a separately auditable action.

