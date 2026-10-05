# OIL-GENESIS-001 — Stage 1 Report

## STAGE

`STAGE 1 — DOMAIN FREEZE`

Result: `PASS — HUMAN SEMANTIC CORRECTION APPLIED`  
Domain decision: `FREEZE`

Human review corrected the initial `OBSERVED → SUPPORTED + metadata` mapping. The final freeze treats `OBSERVED` as its own canonical status, preserves one-to-one status semantics, and requires append-only coexistence of historical `SUPPORTED`, `OBSERVED`, and any later claim-level `CONTRADICTED` decision.

## INPUT

- OIL-DPE v0.4 (frozen)
- Stage 0 architecture decision and implementation mapping
- Authorized worktree: `/Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001`
- Branch: `codex/oil-genesis-001`
- Authoritative base: `f81fcbcbcab4891d0043eee8617f0a7b7f632ad2`
- Twelve candidate claims supplied in the Stage 1 authorization
- Limited official standards/regulation checks for domain viability; no supplier discovery

## DOMAIN_RESULT

- `DOMAIN_ID`: `OIL-DOMAIN-001`
- `DOMAIN_NAME`: Reinforced Platinum-Cured Silicone Hose
- `DOMAIN_VERSION`: `v0.1`
- `TESTABILITY`: `PASS`
- `EVIDENCE_ACCESSIBILITY`: `PASS`
- `REUSE_POTENTIAL`: `PASS`
- `OUTCOME_OBSERVABILITY`: `PASS`
- `REGULATORY_FRICTION`: `PASS` with strict scope controls
- `DOMAIN_DECISION`: `FREEZE`

## CLAIMS_CONSIDERED

12 candidates: C1–C12.

## CLAIMS_FROZEN

7 claims:

1. `OIL-CAP-SIL-001` — platinum_cured
2. `OIL-CAP-SIL-002` — reinforced_construction
3. `OIL-CAP-SIL-003` — maximum_working_pressure
4. `OIL-CAP-SIL-004` — minimum_operating_temperature
5. `OIL-CAP-SIL-005` — maximum_operating_temperature
6. `OIL-CAP-SIL-006` — fda_21_cfr_177_2600_documentation
7. `OIL-CAP-SIL-007` — ec_1935_2004_documentation

## CLAIMS_DEFERRED

- C3 — ID 6 mm / OD 12 mm: exact demand geometry.
- C5 — 25 m continuous length: exact demand/commercial constraint.

Removed from Genesis:

- C4 — 3 mm wall thickness: redundant/configuration-specific and unsafe to infer from nominal dimensions without tolerances.
- C11 — 2007/19/EC: legacy plastics-regime amendment, not a stable standalone silicone-hose Genesis claim.
- C12 — AS 2069: authoritative reference/applicability unresolved; no silent substitution permitted.

## ENUMS_FROZEN

- Canonical status vocabulary: `SUPPORTED`, `OBSERVED`, `UNKNOWN`, `NOT_ESTABLISHED`, `CONTRADICTED`; every value maps one-to-one to itself.
- Status history: append-only; `SUPPORTED` and `OBSERVED` may coexist, and contradictory observations remain preserved if a newer `CONTRADICTED` decision is appended.
- Visibility: `PUBLIC`, `AUTHORIZED_BUYER`, `TRANSACTION_PRIVATE`.
- Demand types: `EXTERNAL_DEMAND`, `OPERATOR_DEMAND`.
- Fact origins: `GENESIS_SUBMISSION`, `SUPPLIER_UPDATE`, `DEMAND_TRIGGERED`, `OUTCOME_GENERATED`, `STRUCTEVIDENCE_RESEARCH`.
- Evidence types: `THIRD_PARTY_CERTIFICATE`, `THIRD_PARTY_TEST_REPORT`, `MANUFACTURER_DATASHEET`, `MANUFACTURER_DECLARATION`, `FACTORY_DOCUMENT`, `PHYSICAL_SAMPLE_OBSERVATION`, `BUYER_TEST`, `TRANSACTION_OUTCOME`, `PUBLIC_CORPORATE_RECORD`.
- Provider status (model only): `IDENTITY_UNVERIFIED`, `IDENTITY_VERIFIED`, `INACTIVE`.
- Stop reasons: `QUALIFYING_DOCUMENT`, `TWO_INDEPENDENT_SOURCES`, `INSUFFICIENT_EVIDENCE`, `MAX_VERIFICATION_TIME`.

## FILES_CREATED

- `docs/open-intent-lab/genesis/OIL_GENESIS_001_DOMAIN_FREEZE.md`
- `data/open-intent-lab/genesis-001/claim-dictionary.json`
- `docs/open-intent-lab/execution/STAGE_01_REPORT.md`
- `scripts/test_oil_genesis_stage1.py`

## FILES_CHANGED

None. Stage 1 adds isolated files only.

## TESTS

The Stage 1 validation suite checks:

- exact domain identity and seven-claim count;
- unique, deterministic claim IDs;
- required claim-definition fields;
- allowed units/operators and evidence-example vocabulary;
- exact one-to-one canonical status mapping, including `OBSERVED → OBSERVED`;
- coexistence of historical `SUPPORTED` and `OBSERVED` records;
- append-only history with historic overwrite explicitly forbidden;
- exact visibility, fact-origin, and evidence-type enums;
- absence of supplier/provider records, demand records, ranking, scores, confidence, capability facts, and duplicate evidence/provenance truth records;
- all required domain-freeze sections;
- no tracked public-case changes relative to the authoritative base.

Executed: `python3 -B scripts/test_oil_genesis_stage1.py`  
Result: `10/10 PASS`. All prior Stage 1 checks remain covered. No database or runtime test is required for this schema-only stage.

## OPEN_GAPS

- All actual provider/product capability statuses remain unknown; no evidence was collected.
- Authorization storage/enforcement for buyer and transaction-private evidence is not implemented.
- “AS 2069” remains unresolved and is not silently replaced.
- Product-specific EU material-measure applicability and temperature test conditions remain future evidence questions.
- Existing repository baseline-test drift identified in Stage 0 is outside this Stage 1 schema-only scope.

## HUMAN_GATE_REQUIRED

`YES`

Stage 2 requires explicit human authorization. This report does not authorize supplier discovery, selection, contact, provider records, capability facts, demand records, migrations, API/UI work, deployment, or public-case edits.

## NEXT_ALLOWED_STAGE

`STAGE_2_SUPPLIER_SELECTION`, only after the human gate is explicitly passed.
