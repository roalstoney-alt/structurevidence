# OIL-GENESIS-001 — Stage 2 Report

## STAGE

`STAGE 2 — SUPPLIER SELECTION`

Result: `PASS`  
Control: `PILOT_SELECTION_ONLY — NOT_MARKET_RANKING`

## SEARCHES_RUN

Eleven recorded query families across twelve official domains/source families, plus official identity, manufacturing, document, and contact-route checks. Full provenance is stored in `data/open-intent-lab/genesis-001/search-runs/stage-2-supplier-discovery.json`.

## ENTITIES_DISCOVERED

`11`

## ENTITIES_DEEPLY_REVIEWED

`10`

## ENTITIES_EXCLUDED

`6` — two credible reserve candidates, one thin evidence chain, one domain mismatch, one insufficient identity chain, and one distributor-only attribution.

## SELECTED_CANDIDATES

1. `OIL-CAND-001` — Venair Ibérica SAU
2. `OIL-CAND-002` — Saint-Gobain Performance Plastics Corporation
3. `OIL-CAND-003` — NewAge Industries, Inc. / AdvantaPure
4. `OIL-CAND-004` — Watson-Marlow Flow Smart, Inc. / BioPure
5. `OIL-CAND-005` — Trelleborg AB (publ) / Trelleborg Medical Solutions

## IDENTITY_VERIFIED_COUNT

`4`; one additional selected candidate is `IDENTITY_PARTIAL` because the exact Trelleborg manufacturing/contracting affiliate remains unresolved.

## MANUFACTURER_COUNT

`5`

## CONTACTABLE_COUNT

`5`; every selected candidate has at least one attributable official route. No contact was attempted.

## PUBLIC_EVIDENCE_SIGNAL_COUNT

`30` public candidate/claim signals across 35 possible pairs. These are discovery signals only.

## FILES_CREATED

- `docs/open-intent-lab/genesis/OIL_GENESIS_001_SUPPLIER_SELECTION.md`
- `data/open-intent-lab/genesis-001/providers/candidate-001.json`
- `data/open-intent-lab/genesis-001/providers/candidate-002.json`
- `data/open-intent-lab/genesis-001/providers/candidate-003.json`
- `data/open-intent-lab/genesis-001/providers/candidate-004.json`
- `data/open-intent-lab/genesis-001/providers/candidate-005.json`
- `data/open-intent-lab/genesis-001/search-runs/stage-2-supplier-discovery.json`
- `scripts/test_oil_genesis_stage2.py`
- `docs/open-intent-lab/execution/STAGE_02_REPORT.md`

## FILES_CHANGED

None. Stage 2 adds isolated artifacts and does not change the Stage 1 dictionary or OIL-DPE v0.4.

## TESTS

Executed: `python3 -B scripts/test_oil_genesis_stage2.py`  
Result: `10/10 PASS`.

The suite verifies exactly five unique candidate records, valid official-domain formats, identity/manufacturer states, official contact routes, controlled public-signal vocabulary, absence of canonical capability states, absence of production Provider/Demand/ranking/score/confidence fields, 30 signal pairs, bounded search provenance, required document sections, and no public-case change.

## OPEN_GAPS

- No supplier document submission or canonical Evidence review has occurred.
- Trelleborg's exact legal manufacturing/contracting affiliate remains unresolved.
- Several exact regulation artifacts remain unavailable or gated.
- Product/size/condition scope must be preserved during any invitation and verification.
- Participation likelihood remains unknown until outreach is separately authorized.

## HUMAN_GATE_REQUIRED

`YES`

Stage 3 requires explicit human authorization. No supplier was contacted and no outreach pack was produced or sent.

## NEXT_ALLOWED_STAGE

`STAGE_3_SUPPLIER_OUTREACH_PACK`, only after the human gate is explicitly passed.

