# Phase 1 Test Report

## New tests

`scripts/test_rdl_research_record.py`

Result: `24/24 PASS`.

Coverage includes all six required fixtures plus Evidence Core reuse, L0 external-research prohibition, failed-research validity, decision delta, UNKNOWN telemetry, estimated/observed separation, evidence-role separation, checked-source discipline, L2/L3 authorization representation, CML authority, customer/privacy boundaries, score prohibition, stop extensions, correction preservation, lookup fields, canonical input/record hash integrity, historical CML preservation, and unchanged RDL freshness files.

## Existing acceptance baselines

| Suite | Result |
| --- | --- |
| CML v1.1 transition | 10/10 PASS |
| CML v1.1 core | 15/15 PASS |
| CML v1.1 regression harness | 6/6 PASS |
| CML v1.1 observation | 16/16 PASS |
| CML v1.1 final audit | 3/3 PASS |
| CML-PDRE-001 lifecycle | 10/10 PASS |
| CML-PDRE-001 EVP-001 | 12/12 PASS |
| RDL freshness policy | PASS |
| RDL freshness runtime | PASS |
| RDL freshness validation | PASS |
| RDL freshness/GDR integration | PASS |

Current CML/pilot baseline remains `72/72 PASS`.

## Pre-existing failures

The Phase 0 full-suite baseline recorded three historical Opportunity Validation failures:

- Phase A fixed history-shape assumption;
- Phase B frozen-baseline comparison against later legitimate state;
- Phase B-R1 accepted Wave 1 baseline comparison against later legitimate state.

Disposition: `PRE_EXISTING_FAILURE / OUT_OF_PHASE_1_SCOPE`.

They were not fixed, modified, or rebaselined as passing. Phase 1 acceptance permits exactly these known failures and no new regression.

Full repository discovery result: `163 run; 160 PASS; 2 failures and 1 error`, consisting exactly of the three pre-existing Opportunity Validation failures above. `NEW_FAILURES = 0`.

## Gate status

`NEW_TESTS = PASS`

`CML_PILOT_BASELINE = PASS`

`RDL_FRESHNESS_BASELINE = PASS`

`FULL_REPOSITORY_REGRESSION = PASS_WITH_3_KNOWN_PRE_EXISTING_FAILURES; 0_NEW_FAILURES`
